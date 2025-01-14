import copy
import os
import json
import traceback
import requests
import concurrent.futures
import zipfile
import urllib

from logging import info, warning, debug, error, critical
from typing import Callable

from pcbnew import *


MODELS_DIR = "EASYEDA_MODELS"

class ComponentLoader():
    def __init__(self, kiprjmod, target_path, target_name, progress: Callable[[int, int], None]):
        self.kiprjmod = kiprjmod
        self.target_path = target_path
        self.target_name = target_name
        self.progress = progress

    def downloadAll(self, components):
        self.progress(0, 100)

        try:
            libDeviceFile, fetched_3dmodels = self.downloadSymFp(components)
            self.downloadModels(libDeviceFile, fetched_3dmodels)
            self.progress(100, 100)
        except Exception as e:
            traceback.print_exc()
            error(f"Failed to download components: {e}")

    def downloadSymFp(self, components):
        info(f"Fetching info...")

        # Find device UUIDs from codes
        resp = requests.post( "https://pro.easyeda.com/api/v2/devices/searchByCodes", data={"codes[]": components} )
        resp.raise_for_status()
        found = resp.json()

        debug("searchByCodes: " + json.dumps( found, indent=4))

        if not found.get("success") or not found.get("result"):
            raise Exception(f"Unabled to fetch device info: {found}")
        
        # Fetch devices by device UUIDs
        fetched_devices = {}

        def fetch_device_info(dev_uuid):
            dev_info = requests.get(f"https://pro.easyeda.com/api/devices/{dev_uuid}")
            dev_info.raise_for_status()

            device = dev_info.json()["result"]
            fetched_devices[device["uuid"]] = device

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for entry in found["result"]:
                dev_uuid = entry['uuid']
                executor.submit(fetch_device_info, dev_uuid)

        # Collect symbol/footprint/3D model UUIDs to fetch
        fetched_symbols = {}
        fetched_footprints = {}
        fetched_3dmodels = {}
        uuid_to_obj_map = {}

        all_uuids = set()
        for entry in fetched_devices.values():
            all_uuids.add(entry['attributes']['Symbol'])
            uuid_to_obj_map[entry['attributes']['Symbol']] = fetched_symbols

            all_uuids.add(entry['attributes']['Footprint'])
            uuid_to_obj_map[entry['attributes']['Footprint']] = fetched_footprints

            if entry['attributes'].get('3D Model'):
                all_uuids.add(entry['attributes']['3D Model'])
                uuid_to_obj_map[entry['attributes']['3D Model']] = fetched_3dmodels

        # Fetch symbols/footprints/3D models
        resp = requests.post( "https://pro.easyeda.com/api/v2/components/searchByIds", json={"uuids": list(all_uuids)} )

        debug("all_uuids: " + json.dumps( list(all_uuids), indent=4))
        debug("searchByIds: " + json.dumps( resp.json(), indent=4))

        for entry in resp.json()["result"]:
            uuid_to_obj_map[entry["uuid"]][entry["uuid"]] = entry

        # Set symbol/footprint type fields
        for device in fetched_devices.values():
            fetched_symbols[device["attributes"]["Symbol"]]["type"] = device["symbol_type"]
            fetched_footprints[device["attributes"]["Footprint"]]["type"] = device["footprint_type"]

        # Extract dataStr
        footprint_data_str = {}
        symbol_data_str = {}

        # Separate dataStr for footprints
        for f_uuid, f_data in fetched_footprints.items():
            ds = f_data.pop("dataStr", None)
            if ds:
                footprint_data_str[f_uuid] = ds

        # Separate dataStr for symbols
        for s_uuid, s_data in fetched_symbols.items():
            ds = s_data.pop("dataStr", None)
            if ds:
                symbol_data_str[s_uuid] = ds

        libDeviceFile = {
            "devices": fetched_devices,
            "symbols": fetched_symbols,
            "footprints": fetched_footprints
        }

        os.makedirs(self.target_path, exist_ok=True)

        zip_filename = f"{self.target_path}/{self.target_name}.elibz"
        merged_data = copy.deepcopy(libDeviceFile)

        try:
            if os.path.exists(zip_filename):
                with zipfile.ZipFile(zip_filename, "r") as old_zip:
                    for name in old_zip.namelist():
                        if name == "device.json":
                            old_data = json.loads(old_zip.read("device.json").decode("utf-8"))
                            for entry_type in ["devices", "symbols", "footprints"]:
                                for key in old_data[entry_type]:
                                    if key not in merged_data[entry_type]:
                                        merged_data[entry_type][key] = old_data[entry_type][key]
                        if name.endswith('.esym'):
                            symbol_uuid = os.path.splitext(os.path.basename(name))[0]
                            if symbol_uuid not in symbol_data_str:
                                symbol_data_str[symbol_uuid] = old_zip.read(name).decode('utf-8')
                        elif name.endswith('.efoo'):
                            footprint_uuid = os.path.splitext(os.path.basename(name))[0]
                            if footprint_uuid not in footprint_data_str:
                                footprint_data_str[footprint_uuid] = old_zip.read(name).decode('utf-8')
        except Exception as e:
            warning(f"Failed to merge device.json data, overwriting: {e}")

        with zipfile.ZipFile(zip_filename, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("device.json", json.dumps(merged_data, indent=4))
            for fp_uuid, ds in footprint_data_str.items():
                zf.writestr(f"FOOTPRINT/{fp_uuid}.efoo", ds)
            for sym_uuid, ds in symbol_data_str.items():
                zf.writestr(f"SYMBOL/{sym_uuid}.esym", ds)

        info(f"Library saved: {zip_filename}")
        return libDeviceFile, fetched_3dmodels

    def downloadModels(self, libDeviceFile, fetched_3dmodels):
        self.totalToDownload = 0
        self.downloadedCounter = 0
        self.statExisting = 0
        self.statDownloaded = 0
        self.statFailed = 0

        info(f"Loading 3D models...")
        self.progress(0, 100)

        uuidToTargetFileMap = {}
        uuidsToDimensions = {}

        debug(json.dumps(fetched_3dmodels, indent=4))

        for device in libDeviceFile["devices"].values():
            try:
                modelUuid = device["attributes"].get("3D Model")

                if not modelUuid or modelUuid not in fetched_3dmodels:
                    info("No model for device '%s', footprint '%s'" % (device.get("product_code"), device.get("footprint").get("display_title")))
                    continue

                debug("Device: " + json.dumps(device, indent=4))

                modelTitle = device["attributes"]["3D Model Title"]
                modelTransform = device["attributes"].get("3D Model Transform", "")

                directUuid = json.loads(fetched_3dmodels[modelUuid]["dataStr"])["model"]

                uuidsToDimensions[directUuid] = [float(x) for x in modelTransform.split(",")]

                easyEdaFilename = os.path.join(self.kiprjmod, MODELS_DIR, modelTitle + ".step")
                easyEdaFilename = os.path.normpath(easyEdaFilename)

                uuidToTargetFileMap[directUuid] = easyEdaFilename
            except KeyboardInterrupt:
                return
            except Exception as e:
                traceback.print_exc()
                info("Cannot get model for device '%s': %s" % (device.get("product_code"), str(e)))
                continue

        with concurrent.futures.ThreadPoolExecutor(1) as texecutor:
            def fixupModel(fixTaskArgs):
                directUuid, kfilePath = fixTaskArgs

                file_name = os.path.splitext( os.path.basename( kfilePath ) ) [0]
                jfilePath = kfilePath + "_jlc"

                debug( "Loading STEP model %s" % (file_name) )
                model: UTILS_STEP_MODEL = UTILS_STEP_MODEL.LoadSTEP(jfilePath)

                if not model:
                    error( "Error loading model '%s'" % (file_name) )
                    return
                
                debug( "Converting STEP model '%s'" % (file_name) )
                bbox: UTILS_BOX3D = model.GetBoundingBox()

                try:
                    if directUuid in uuidsToDimensions:
                        # Convert mils to mm
                        fitXmm = uuidsToDimensions[directUuid][0] / 39.37
                        fitYmm = uuidsToDimensions[directUuid][1] / 39.37

                        bsize: VECTOR3D = bbox.GetSize()
                        scaleFactorX = fitXmm / bsize.x;
                        scaleFactorY = fitYmm / bsize.y;
                        scaleFactor = ( scaleFactorX + scaleFactorY ) / 2

                        debug( "Dimensions %f %f factors %f %f avg %f model '%s'" %
                            (fitXmm, fitYmm, scaleFactorX, scaleFactorY, scaleFactor, file_name) )

                        if abs( scaleFactorX - scaleFactorY ) > 0.1:
                            warning( "Scale factors do not match: X %.3f; Y %.3f for model '%s'." %
                                (scaleFactorX, scaleFactorY, file_name) )
                            warning( "**** The model '%s' might be misoriented! ****" % (file_name) )
                        elif abs( scaleFactor - 1.0 ) > 0.01:
                            warning( "Scaling '%s' by %f" % (file_name, scaleFactor) )
                            model.Scale( scaleFactor );
                        else:
                            debug( "No scaling for %s" % (file_name) )

                except Exception as e:
                    traceback.print_exc()
                    error( "Error scaling model '%s': %s" % (file_name, str(e)) )
                    return

                newbbox          = model.GetBoundingBox()
                center: VECTOR3D = newbbox.GetCenter()

                model.Translate( -center.x, -center.y, -newbbox.Min().z )

                debug( "Saving STEP model %s" % (file_name) )
                model.SaveSTEP( kfilePath )

            with concurrent.futures.ThreadPoolExecutor(8) as dexecutor: 
                def downloadStep(dnlTaskArgs):
                    directUuid, kfilePath = dnlTaskArgs
                    file_name = os.path.splitext( os.path.basename( kfilePath ) ) [0]

                    try:
                        if not os.path.exists(kfilePath):
                            stepUrlFormat = "https://modules.easyeda.com/qAxj6KHrDKw4blvCG8QJPs7Y/{uuid}"
                            jfilePath = kfilePath + "_jlc"
                            url = stepUrlFormat.format(uuid=directUuid)

                            debug("Downloading '%s'" % (file_name))
                            debug("'%s' from '%s'" % (file_name, url))
                            os.makedirs(os.path.dirname(kfilePath), exist_ok=True)
                            urllib.request.urlretrieve(url, jfilePath)

                            if os.path.isfile(jfilePath):
                                debug("Downloaded '%s'." % (file_name))
                                self.statDownloaded += 1

                                fixTaskArgs = [directUuid, kfilePath]
                                texecutor.submit(fixupModel, fixTaskArgs)
                            else:
                                warning( "Path '%s' is not a file." % jfilePath )
                        else:
                            info("Skipping '%s': STEP model file already exists." % (file_name))
                            self.statExisting += 1

                    except Exception as e:
                        warning("Failed to download model '%s': %s" % (file_name, str(e)))
                        self.statFailed += 1

                    self.downloadedCounter += 1
                    self.progress(self.downloadedCounter, self.totalToDownload)

                self.totalToDownload = len(uuidToTargetFileMap)
                dexecutor.map(downloadStep, uuidToTargetFileMap.items())

        info( "" )
        info( "*****************************" )
        info( "          All done.          " )
        info( "*****************************" )
        info( "" )
        info( "Total model count: %d" % len(uuidToTargetFileMap) )
        info( "STEP models downloaded: %d" % self.statDownloaded )
        info( "Already existing models: %d" % self.statExisting )
        info( "Failed downloads: %d" % self.statFailed )
        self.progress(100, 100)
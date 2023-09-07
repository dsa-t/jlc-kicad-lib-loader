#!/usr/bin/env python

import sys
import os
import json
import requests
import urllib.request
import concurrent.futures
import logging
import wx

from threading import Lock, Thread
from logging import info, warn, debug, error, critical
from typing import Callable
from io import StringIO

from .easyeda_3d_loader_dialog import EasyEda3DLoaderDialog 
from pcbnew import *

DIRECT_MODEL_UUID_KEY = "JLC_3DModel"
QUERY_MODEL_UUID_KEY = "JLC_3DModel_Q"
MODEL_SIZE_KEY = "JLC_3D_Size"

MODELS_DIR = "EASYEDA_MODELS"

log_stream = StringIO()    
logging.basicConfig(stream=log_stream, level=logging.INFO)

slock = Lock()
dlock = Lock()

global totalToDownload
totalToDownload = 0;

global downloadedCounter
downloadedCounter = 0;

global statDownloaded
statDownloaded = 0

global statExisting
statExisting = 0

global statFailed
statFailed = 0

def downloadModels( pcb: BOARD, progress: Callable[[int, int], None] = lambda a, b: None ):
    global downloadedCounter
    global statDownloaded
    global statExisting
    global statFailed
    
    kiprjmod = os.getenv("KIPRJMOD") or ""

    if not kiprjmod:
        error( "KIPRJMOD is not set properly. Exiting." )
        exit(1)

    totalToDownload = 0
    downloadedCounter = 0
    statExisting = 0
    statDownloaded = 0
    statFailed = 0

    progress(0, 100)

    footprints: list[FOOTPRINT]
    footprints = pcb.GetFootprints()

    uuidsMap = {}
    uuidsToDimensions = {}
    uuidsToQuery = set()

    for footprint in footprints:
        if footprint.HasField( QUERY_MODEL_UUID_KEY ):
            uuidsToQuery.add( footprint.GetFieldText(QUERY_MODEL_UUID_KEY) )

    if len( uuidsToQuery ) > 0:
        
        def doQuery( queryUuidList ):
            url = "https://pro.lceda.cn/api/components/searchByIds?forceOnline=1"
            form_data = {
                'uuids[]': queryUuidList,
                'dataStr': 'yes'
            }

            debug(str(form_data))
            resp = requests.post(url, data=form_data)
            respJson = resp.json()
            debug(json.dumps(respJson))

            result = respJson["result"]

            for entry in result:
                try:
                    data = json.loads( entry["dataStr"] )
                    directUuid = data["model"]
                    uuidsMap[entry["uuid"]] = directUuid
                except Exception as e:
                    debug(e)
                    warn("Cannot parse entry")

            return result
            
        info( "Requesting UUID info..." )
        try:
            for uuid in uuidsToQuery:
                uuidsMap[uuid] = uuid # Default (direct) mapping

            result = doQuery(uuidsToQuery)

            if len(result) == 0:
                debug( "Response result is empty" )

            debug( uuidsMap )
        except Exception as e:
            error(e)
            error( "Cannot query direct model UUIDs" )

    uuidToTargetFileMap = {}

    for footprint in footprints:
        directUuid = ""

        if footprint.HasField( DIRECT_MODEL_UUID_KEY ):
            directUuid = footprint.GetFieldText( DIRECT_MODEL_UUID_KEY )

        if footprint.HasField( QUERY_MODEL_UUID_KEY ):
            directUuid = uuidsMap.get( footprint.GetFieldText( QUERY_MODEL_UUID_KEY ) )

        if not directUuid:
            info("Cannot find model for footprint '%s'" % (footprint.GetReference()))
            continue

        if footprint.HasField( MODEL_SIZE_KEY ):
            value: str = footprint.GetFieldText( MODEL_SIZE_KEY )
            uuidsToDimensions[directUuid] = [float(x) for x in value.split(" ")];

        models: VECTOR_FP_3DMODEL = footprint.Models();
        easyEdaFilename = None
    
        for _it in models:
            mod: FP_3DMODEL = _it;
            fname: str = mod.m_Filename

            if MODELS_DIR in fname:
                easyEdaFilename = fname
                break;
        
        if not easyEdaFilename:
            info("Did non find a 3D model path containing '%s' for footprint '%s'" % (MODELS_DIR, footprint.GetReference()))
            continue

        easyEdaFilename = easyEdaFilename.replace( "${KIPRJMOD}", kiprjmod )
        easyEdaFilename = os.path.normpath(easyEdaFilename)

        uuidToTargetFileMap[directUuid] = easyEdaFilename

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

            if directUuid in uuidsToDimensions:
                [fitXmm, fitYmm] = uuidsToDimensions[directUuid]
                bsize: VECTOR3D = bbox.GetSize()
                scaleFactorX = fitXmm / bsize.x;
                scaleFactorY = fitYmm / bsize.y;
                scaleFactor = ( scaleFactorX + scaleFactorY ) / 2

                debug( "Dimensions %f %f factors %f %f avg %f model '%s'" %
                      (fitXmm, fitYmm, scaleFactorX, scaleFactorY, scaleFactor, file_name) )

                if abs( scaleFactorX - scaleFactorY ) > 0.1:
                    warn( "Scale factors do not match: X %.3f; Y %.3f for model '%s'." %
                         (scaleFactorX, scaleFactorY, file_name) )
                    warn( "**** The model '%s' might be misoriented! ****" % (file_name) )
                elif abs( scaleFactor - 1.0 ) > 0.01:
                    warn( "Scaling '%s' by %f" % (file_name, scaleFactor) )
                    model.Scale( scaleFactor );
                else:
                    debug( "No scaling for %s" % (file_name) )

            newbbox          = model.GetBoundingBox()
            center: VECTOR3D = newbbox.GetCenter()

            model.Translate( -center.x, -center.y, -newbbox.Min().z )

            debug( "Saving STEP model %s" % (file_name) )
            model.SaveSTEP( kfilePath )

        with concurrent.futures.ThreadPoolExecutor(8) as dexecutor: 
            def downloadStep(dnlTaskArgs):
                global downloadedCounter
                global statDownloaded
                global statExisting
                global statFailed
                
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
                            
                            with slock:
                                statDownloaded += 1

                            fixTaskArgs = [directUuid, kfilePath]
                            texecutor.submit(fixupModel, fixTaskArgs)
                        else:
                            warn( "Path '%s' is not a file." % jfilePath )
                    else:
                        info("Skipping '%s': STEP model file already exists." % (file_name))

                        with slock:
                            statExisting += 1

                except Exception as e:
                    warn("Failed to download model '%s': %s" % (file_name, str(e)))

                    with slock:
                        statFailed += 1

                with dlock:
                    downloadedCounter += 1
                    progress(downloadedCounter, totalToDownload)

            totalToDownload = len(uuidToTargetFileMap)
            dexecutor.map(downloadStep, uuidToTargetFileMap.items())

    info( "" )
    info( "*****************************" )
    info( "          All done.          " )
    info( "*****************************" )
    info( "" )
    info( "Total model count: %d" % len(uuidToTargetFileMap) )
    info( "STEP models downloaded: %d" % statDownloaded )
    info( "Already existing models: %d" % statExisting )
    info( "Failed downloads: %d" % statFailed )
    progress(100, 100)

if len( sys.argv ) > 1:
    filename = sys.argv[1]

    absPath = os.path.abspath(filename);
    pcb = LoadBoard(absPath)

    if not os.getenv("KIPRJMOD"):
        os.environ["KIPRJMOD"] = os.path.dirname(absPath)

    downloadModels(pcb)
    exit(0)

class WxTextCtrlHandler(logging.Handler):
    def __init__(self, ctrl: wx.TextCtrl):
        logging.Handler.__init__(self)
        self.ctrl = ctrl

    def emit(self, record):
        s = self.format(record) + '\n'
        wx.CallAfter(self.ctrl.AppendText, s)

class EasyEDALoaderPlugin(ActionPlugin):
    thread: Thread | None = None
    
    def defaults(self):
        self.name = "EasyEDA (JLCEDA) 3D Model Loader"
        self.category = "3D data loader"
        self.description = "Load STEP 3D models for EasyEDA (JLCEDA) PCB"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'easyeda_3d_loader.png')

    def Run(self):
        dlg = EasyEda3DLoaderDialog(None)

        handler = WxTextCtrlHandler(dlg.m_log)
        logging.getLogger().handlers.clear();
        logging.getLogger().addHandler(handler)
        FORMAT = "%(levelname)s: %(message)s"
        handler.setFormatter(logging.Formatter(FORMAT))
        logging.getLogger().setLevel(level=logging.INFO)

        def progressHandler( current, total ):
            wx.CallAfter(dlg.m_progress.SetRange, total)
            wx.CallAfter(dlg.m_progress.SetValue, current)

        def onDebugCheckbox( event: wx.CommandEvent ):
            logging.getLogger().setLevel( logging.DEBUG if event.IsChecked() else logging.INFO )

        def onDownloadAndFixup( event ):
            dlg.m_log.Clear()

            def threadedFn(): 
                pcb: BOARD = GetBoard()
                downloadModels(pcb, progressHandler)
                wx.CallAfter(dlg.m_actionBtn.Enable)
                wx.CallAfter(dlg.m_closeBtn.SetFocus)

            dlg.m_actionBtn.Disable()
            self.thread = Thread(target = threadedFn)
            self.thread.daemon = True
            self.thread.start()

        def onClose( event ):
            if self.thread:
                self.thread.join( 0.1 )

                if self.thread.is_alive():
                    # TODO: terminate thread
                    return
                
            dlg.Destroy();

        dlg.SetEscapeId(wx.ID_CANCEL)
        dlg.m_actionBtn.Bind(wx.EVT_BUTTON, onDownloadAndFixup)
        dlg.m_closeBtn.Bind(wx.EVT_BUTTON, onClose)
        dlg.m_debug.Bind(wx.EVT_CHECKBOX, onDebugCheckbox)
        dlg.Show()

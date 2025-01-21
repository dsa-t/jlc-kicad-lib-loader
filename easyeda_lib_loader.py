#!/usr/bin/env python

import math
import sys
import os
import traceback
import requests
import logging
import wx

wx_html2_available = True
try: 
    import wx.html2
except ImportError as e:
    wx_html2_available = False

from threading import Lock, Thread
from logging import info, warning, debug, error, critical
from io import StringIO

import wx.dataview

from .component_loader import *
from .easyeda_lib_loader_dialog import EasyEdaLibLoaderDialog

from pcbnew import *
import ctypes

log_stream = StringIO()    
logging.basicConfig(stream=log_stream, level=logging.INFO)

def interrupt_thread(thread):
    print("interrupt_thread")
    if not thread.is_alive():
        return

    exc = ctypes.py_object(KeyboardInterrupt)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)

    if res == 0:
        print("nonexistent thread id")
        return False
    elif res > 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        print("PyThreadState_SetAsyncExc failed")

        return False
    
    print("interrupt_thread success")
    return True


class WxTextCtrlHandler(logging.Handler):
    def __init__(self, ctrl: wx.TextCtrl):
        logging.Handler.__init__(self)
        self.ctrl = ctrl

    def emit(self, record):
        s = self.format(record) + '\n'
        wx.CallAfter(self.ctrl.AppendText, s)

class EasyEDALibLoaderPlugin(ActionPlugin):
    downloadThread: Thread | None = None
    searchThread: Thread | None = None
    searchPage = 1
    components = []
    
    def defaults(self):
        self.name = "EasyEDA (LCEDA) Library Loader"
        self.category = "3D data loader"
        self.description = "Load library parts from EasyEDA (LCEDA)"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'easyeda_lib_loader.png')

    def Run(self):
        dlg = EasyEdaLibLoaderDialog(None)

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

        def onDownload( event ):
            dlg.m_log.Clear()

            if not dlg.m_textCtrlParts.GetValue().strip():
                for sel in dlg.m_searchResultsTree.GetSelections():
                    dlg.m_textCtrlParts.AppendText(dlg.m_searchResultsTree.GetItemText(sel) + "\n")

            components = dlg.m_textCtrlParts.GetValue().splitlines()

            if not components:
                error( "No parts to download." )
                return

            kiprjmod = os.getenv("KIPRJMOD") or ""

            if not kiprjmod:
                error( "KIPRJMOD is not set properly." )
                return
            
            lib_field = dlg.m_textCtrlOutLibName.GetValue()
            
            if os.path.isabs(lib_field):
                target_path = lib_field
            else:
                target_path = os.path.join(kiprjmod, lib_field)

            target_name = os.path.basename(target_path);

            def threadedFn():
                loader = ComponentLoader(kiprjmod=kiprjmod, target_path=target_path, target_name=target_name, progress=progressHandler)
                loader.downloadAll(components)

                wx.CallAfter(dlg.m_actionBtn.Enable)

            dlg.m_actionBtn.Disable()
            self.downloadThread = Thread(target = threadedFn, daemon=True)
            self.downloadThread.start()

        def searchFn(facet, words, page):
            def setStatus( status ):
                wx.CallAfter(dlg.m_searchStatus.SetLabel, status)
                wx.CallAfter(dlg.m_statusPanel.Layout)

            def setPageText( pageText ):
                wx.CallAfter(dlg.m_searchPage.SetLabel, pageText)
                wx.CallAfter(dlg.m_statusPanel.Layout)

            def clearItems():
                wx.CallAfter(dlg.m_searchResultsTree.DeleteAllItems)

            def appendItem( data ):
                treeItem = dlg.m_searchResultsTree.AppendItem( dlg.m_searchResultsTree.GetRootItem(), data[0] )

                for i in range(1, len(data)):
                    dlg.m_searchResultsTree.SetItemText(treeItem, i, data[i]);

            def addItem( item ):
                wx.CallAfter(appendItem, item)


            setStatus("Searching...")
            clearItems()

            wx.CallAfter(dlg.m_prevPageBtn.Disable)
            wx.CallAfter(dlg.m_nextPageBtn.Disable)

            try:
                pageSize = 50

                resp = requests.post( "https://pro.easyeda.com/api/v2/devices/search", 
                                        data={
                                            "page": page,
                                            "pageSize": pageSize,
                                            "wd": words,
                                            "returnListStyle": "classifyarr"
                                            } )
                resp.raise_for_status()
                found = resp.json()

                if not found.get("success") or not found.get("result"):
                    raise Exception(f"Unable to search: {found}")

                totalInFacet = found["result"]["facets"].get(facet, 0)

                for entry in found["result"]["lists"][facet]:
                    addItem([
                        entry["product_code"],
                        entry["display_title"],
                        entry["attributes"]["Manufacturer"],
                        entry["symbol"]["display_title"],
                        entry["footprint"]["display_title"]
                    ])

                curPage = int(found['result']['page'])
                totalPages = math.ceil(totalInFacet / pageSize)

                if(curPage > 1):
                    wx.CallAfter(dlg.m_prevPageBtn.Enable)

                if(curPage < totalPages):
                    wx.CallAfter(dlg.m_nextPageBtn.Enable)

                setStatus(f"{totalInFacet} parts.")
                setPageText(f"Page {curPage}/{totalPages}")

            except KeyboardInterrupt:
                print("KeyboardInterrupt.")
            except Exception as e:
                traceback.print_exc()
                setStatus(f"Failed to search parts: {e}")

            finally:
                self.searchThread = None

        def loadSearchPage( facetId, words, page ):
            if self.searchThread:
                interrupt_thread(self.searchThread)
                self.searchThread.join()

            facet = ["lcsc", "user"][facetId]

            self.searchThread = Thread(target = searchFn, 
                                 daemon=True, 
                                 args=(facet, words, page))
            self.searchThread.start()

        def onSearch( event ):
            self.searchPage = 1
            loadSearchPage(dlg.m_libSourceChoice.GetSelection(), dlg.m_textCtrlSearch.GetValue(), self.searchPage)

        def onNextPage( event ):
            self.searchPage += 1
            loadSearchPage(dlg.m_libSourceChoice.GetSelection(), dlg.m_textCtrlSearch.GetValue(), self.searchPage)
        
        def onPrevPage( event ):
            self.searchPage -= 1
            loadSearchPage(dlg.m_libSourceChoice.GetSelection(), dlg.m_textCtrlSearch.GetValue(), self.searchPage)

        def onSearchItemActivated( event ):
            if dlg.m_textCtrlParts.GetValue() and not dlg.m_textCtrlParts.GetValue().endswith("\n"):
                dlg.m_textCtrlParts.AppendText("\n")

            dlg.m_textCtrlParts.AppendText(dlg.m_searchResultsTree.GetItemText(event.GetItem()) + "\n")

        def onSearchItemSelected( event ):
            itemCode = dlg.m_searchResultsTree.GetItemText(event.GetItem())

            dlg.m_searchHyperlink1.SetLabelText( f"{itemCode} Preview" )
            dlg.m_searchHyperlink1.SetURL( f"https://jlcpcb.com/user-center/lcsvg/svg.html?code={itemCode}" )

            dlg.m_searchHyperlink2.SetLabelText( f"JLCPCB" )
            dlg.m_searchHyperlink2.SetURL( f"https://jlcpcb.com/partdetail/{itemCode}" )

            dlg.m_searchHyperlink3.SetLabelText( f"LCSC" )
            dlg.m_searchHyperlink3.SetURL( f"https://www.lcsc.com/product-detail/{itemCode}.html" )

            dlg.m_statusPanel.Layout()

            global wx_html2_available
            if wx_html2_available:
                self.webView.Hide()
                self.webView.LoadURL( f"https://jlcpcb.com/user-center/lcsvg/svg.html?code={itemCode}" )
                self.webView.SetZoomFactor(0.8)

        def onWebviewLoaded( event ):
            self.webView.Show()

        def onClose( event ):
            if self.searchThread:
                interrupt_thread(self.searchThread)
                self.searchThread.join( 5 )
                
            if self.downloadThread:
                interrupt_thread(self.downloadThread)
                self.downloadThread.join( 5 )
                
            dlg.Destroy();

        dlg.m_searchResultsTree.AppendColumn("Code", width=wx.COL_WIDTH_AUTOSIZE, flags=wx.COL_RESIZABLE | wx.COL_SORTABLE )
        dlg.m_searchResultsTree.AppendColumn("Name", width=wx.COL_WIDTH_AUTOSIZE, flags=wx.COL_RESIZABLE | wx.COL_SORTABLE)
        dlg.m_searchResultsTree.AppendColumn("Manufacturer", width=wx.COL_WIDTH_AUTOSIZE, flags=wx.COL_RESIZABLE | wx.COL_SORTABLE)
        dlg.m_searchResultsTree.AppendColumn("Symbol", width=wx.COL_WIDTH_AUTOSIZE, flags=wx.COL_RESIZABLE | wx.COL_SORTABLE)
        dlg.m_searchResultsTree.AppendColumn("Footprint", width=wx.COL_WIDTH_AUTOSIZE, flags=wx.COL_RESIZABLE | wx.COL_SORTABLE)

        dlg.m_textCtrlOutLibName.SetValue("EasyEDA_Lib");

        global wx_html2_available
        if wx_html2_available:
            try:
                self.webView = wx.html2.WebView.New(dlg.m_webViewPanel)
                self.webView.Bind(wx.html2.EVT_WEBVIEW_LOADED, onWebviewLoaded)
            except NotImplementedError as err:
                self.webView = wx.StaticText(dlg.m_webViewPanel, style=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTRE_HORIZONTAL)
                self.webView.SetLabel("Preview is not supported in this wxPython environment.")
                dlg.m_webViewPanel.SetMinSize( wx.Size(20, 20) )
                wx_html2_available = False
        else:
            self.webView = wx.StaticText(dlg.m_webViewPanel, style=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTRE_HORIZONTAL)
            self.webView.SetLabel("wx.html2 is not available. Install python3-wxgtk-webview4.0 (Debian/Ubuntu)")
            dlg.m_webViewPanel.SetMinSize( wx.Size(20, 20) )

        dlg.m_webViewPanel.GetSizer().Add(self.webView, 1, wx.EXPAND)
        dlg.m_webViewPanel.Layout()

        dlg.SetEscapeId(wx.ID_CANCEL)
        dlg.Bind(wx.EVT_CLOSE, onClose)
        
        dlg.m_searchResultsTree.Bind(wx.dataview.EVT_TREELIST_ITEM_ACTIVATED, onSearchItemActivated)
        dlg.m_searchResultsTree.Bind(wx.dataview.EVT_TREELIST_SELECTION_CHANGED, onSearchItemSelected)
        dlg.m_actionBtn.Bind(wx.EVT_BUTTON, onDownload)
        dlg.m_searchBtn.Bind(wx.EVT_BUTTON, onSearch)
        dlg.m_prevPageBtn.Bind(wx.EVT_BUTTON, onPrevPage)
        dlg.m_nextPageBtn.Bind(wx.EVT_BUTTON, onNextPage)
        dlg.m_textCtrlSearch.Bind(wx.EVT_TEXT_ENTER, onSearch)
        dlg.m_debug.Bind(wx.EVT_CHECKBOX, onDebugCheckbox)

        dlg.m_textCtrlSearch.SetFocus()
        dlg.Show()

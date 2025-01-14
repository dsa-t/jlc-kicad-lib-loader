# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.dataview
import wx.adv

###########################################################################
## Class EasyEdaLibLoaderDialog
###########################################################################

class EasyEdaLibLoaderDialog ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"JLCPCB/LCSC Library Loader. Unofficial, use at your own risk.", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer6 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_splitter2 = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D|wx.SP_LIVE_UPDATE )
		self.m_splitter2.SetSashGravity( 1 )
		self.m_splitter2.Bind( wx.EVT_IDLE, self.m_splitter2OnIdle )
		self.m_splitter2.SetMinimumPaneSize( 100 )

		self.m_leftPanel = wx.Panel( self.m_splitter2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer4 = wx.BoxSizer( wx.VERTICAL )

		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

		m_libSourceChoiceChoices = [ u"JLC System", u"JLC Public" ]
		self.m_libSourceChoice = wx.Choice( self.m_leftPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_libSourceChoiceChoices, 0 )
		self.m_libSourceChoice.SetSelection( 0 )
		self.m_libSourceChoice.Hide()

		bSizer5.Add( self.m_libSourceChoice, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.m_textCtrlSearch = wx.TextCtrl( self.m_leftPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		bSizer5.Add( self.m_textCtrlSearch, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.m_searchBtn = wx.Button( self.m_leftPanel, wx.ID_ANY, u"Find", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer5.Add( self.m_searchBtn, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


		bSizer4.Add( bSizer5, 0, wx.EXPAND, 5 )

		self.m_splitter5 = wx.SplitterWindow( self.m_leftPanel, wx.ID_ANY, wx.DefaultPosition, wx.Size( 650,680 ), wx.SP_3D|wx.SP_LIVE_UPDATE )
		self.m_splitter5.SetSashGravity( 0 )
		self.m_splitter5.Bind( wx.EVT_IDLE, self.m_splitter5OnIdle )
		self.m_splitter5.SetMinimumPaneSize( 100 )

		self.m_statusPanel = wx.Panel( self.m_splitter5, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer18 = wx.BoxSizer( wx.VERTICAL )

		self.m_searchResultsTree = wx.dataview.TreeListCtrl( self.m_statusPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.dataview.TL_MULTIPLE )
		self.m_searchResultsTree.SetMinSize( wx.Size( 400,300 ) )


		bSizer18.Add( self.m_searchResultsTree, 1, wx.EXPAND |wx.ALL, 5 )

		bStatusSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.m_searchStatus = wx.StaticText( self.m_statusPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_searchStatus.Wrap( -1 )

		bStatusSizer.Add( self.m_searchStatus, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.m_searchStatus2 = wx.StaticText( self.m_statusPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_searchStatus2.Wrap( -1 )

		bStatusSizer.Add( self.m_searchStatus2, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP, 2 )

		self.m_searchHyperlink1 = wx.adv.HyperlinkCtrl( self.m_statusPanel, wx.ID_ANY, wx.EmptyString, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.adv.HL_DEFAULT_STYLE )
		bStatusSizer.Add( self.m_searchHyperlink1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.m_searchHyperlink2 = wx.adv.HyperlinkCtrl( self.m_statusPanel, wx.ID_ANY, wx.EmptyString, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.adv.HL_DEFAULT_STYLE )
		bStatusSizer.Add( self.m_searchHyperlink2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.m_searchHyperlink3 = wx.adv.HyperlinkCtrl( self.m_statusPanel, wx.ID_ANY, wx.EmptyString, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.adv.HL_DEFAULT_STYLE )
		bStatusSizer.Add( self.m_searchHyperlink3, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.m_searchPage = wx.StaticText( self.m_statusPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_searchPage.Wrap( -1 )

		bStatusSizer.Add( self.m_searchPage, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.m_prevPageBtn = wx.Button( self.m_statusPanel, wx.ID_ANY, u"  <  ", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		self.m_prevPageBtn.Enable( False )

		bStatusSizer.Add( self.m_prevPageBtn, 0, wx.TOP|wx.BOTTOM, 5 )

		self.m_nextPageBtn = wx.Button( self.m_statusPanel, wx.ID_ANY, u"  >  ", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		self.m_nextPageBtn.Enable( False )

		bStatusSizer.Add( self.m_nextPageBtn, 0, wx.TOP|wx.BOTTOM|wx.RIGHT, 5 )


		bSizer18.Add( bStatusSizer, 0, wx.EXPAND, 5 )


		self.m_statusPanel.SetSizer( bSizer18 )
		self.m_statusPanel.Layout()
		bSizer18.Fit( self.m_statusPanel )
		self.m_webViewPanel = wx.Panel( self.m_splitter5, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_webViewPanel.SetMinSize( wx.Size( 650,380 ) )

		bSizer19 = wx.BoxSizer( wx.VERTICAL )


		self.m_webViewPanel.SetSizer( bSizer19 )
		self.m_webViewPanel.Layout()
		bSizer19.Fit( self.m_webViewPanel )
		self.m_splitter5.SplitHorizontally( self.m_statusPanel, self.m_webViewPanel, 0 )
		bSizer4.Add( self.m_splitter5, 1, wx.EXPAND, 5 )


		self.m_leftPanel.SetSizer( bSizer4 )
		self.m_leftPanel.Layout()
		bSizer4.Fit( self.m_leftPanel )
		self.m_panel1 = wx.Panel( self.m_splitter2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer13 = wx.BoxSizer( wx.VERTICAL )

		self.m_splitter3 = wx.SplitterWindow( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D|wx.SP_LIVE_UPDATE )
		self.m_splitter3.SetSashGravity( 0.5 )
		self.m_splitter3.Bind( wx.EVT_IDLE, self.m_splitter3OnIdle )
		self.m_splitter3.SetMinimumPaneSize( 100 )

		self.m_panel5 = wx.Panel( self.m_splitter3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText1 = wx.StaticText( self.m_panel5, wx.ID_ANY, u"Enter JLCPCB/LCSC codes to download:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )

		bSizer1.Add( self.m_staticText1, 0, wx.ALL, 5 )

		self.m_textCtrlParts = wx.TextCtrl( self.m_panel5, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		bSizer1.Add( self.m_textCtrlParts, 1, wx.ALL|wx.EXPAND, 5 )

		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText2 = wx.StaticText( self.m_panel5, wx.ID_ANY, u"Library path:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )

		bSizer3.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.m_textCtrlOutLibName = wx.TextCtrl( self.m_panel5, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_textCtrlOutLibName, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )


		bSizer1.Add( bSizer3, 0, wx.EXPAND, 5 )

		self.m_actionBtn = wx.Button( self.m_panel5, wx.ID_ANY, u"Download parts", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer1.Add( self.m_actionBtn, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


		self.m_panel5.SetSizer( bSizer1 )
		self.m_panel5.Layout()
		bSizer1.Fit( self.m_panel5 )
		self.m_panel6 = wx.Panel( self.m_splitter3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer14 = wx.BoxSizer( wx.VERTICAL )

		self.m_progress = wx.Gauge( self.m_panel6, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
		self.m_progress.SetValue( 0 )
		bSizer14.Add( self.m_progress, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_log = wx.TextCtrl( self.m_panel6, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_BESTWRAP|wx.TE_MULTILINE|wx.TE_READONLY )
		self.m_log.SetMinSize( wx.Size( 400,40 ) )

		bSizer14.Add( self.m_log, 1, wx.ALL|wx.EXPAND, 5 )

		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_debug = wx.CheckBox( self.m_panel6, wx.ID_ANY, u"Debug", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.m_debug, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )


		bSizer14.Add( bSizer2, 0, wx.EXPAND, 5 )


		self.m_panel6.SetSizer( bSizer14 )
		self.m_panel6.Layout()
		bSizer14.Fit( self.m_panel6 )
		self.m_splitter3.SplitHorizontally( self.m_panel5, self.m_panel6, 0 )
		bSizer13.Add( self.m_splitter3, 1, wx.EXPAND, 5 )


		self.m_panel1.SetSizer( bSizer13 )
		self.m_panel1.Layout()
		bSizer13.Fit( self.m_panel1 )
		self.m_splitter2.SplitVertically( self.m_leftPanel, self.m_panel1, 650 )
		bSizer6.Add( self.m_splitter2, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer6 )
		self.Layout()
		bSizer6.Fit( self )

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass

	def m_splitter2OnIdle( self, event ):
		self.m_splitter2.SetSashPosition( 650 )
		self.m_splitter2.Unbind( wx.EVT_IDLE )

	def m_splitter5OnIdle( self, event ):
		self.m_splitter5.SetSashPosition( 0 )
		self.m_splitter5.Unbind( wx.EVT_IDLE )

	def m_splitter3OnIdle( self, event ):
		self.m_splitter3.SetSashPosition( 0 )
		self.m_splitter3.Unbind( wx.EVT_IDLE )



# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx

###########################################################################
## Class EasyEda3DLoaderDialog
###########################################################################

class EasyEda3DLoaderDialog ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"EasyEDA (JLCEDA) 3D Loader", pos = wx.DefaultPosition, size = wx.Size( 681,427 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.m_actionBtn = wx.Button( self, wx.ID_ANY, u"Download and convert STEP 3D models from JLC", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer1.Add( self.m_actionBtn, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )

		self.m_progress = wx.Gauge( self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
		self.m_progress.SetValue( 0 )
		bSizer1.Add( self.m_progress, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_log = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_BESTWRAP|wx.TE_MULTILINE|wx.TE_READONLY )
		bSizer1.Add( self.m_log, 1, wx.ALL|wx.EXPAND, 5 )

		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_debug = wx.CheckBox( self, wx.ID_ANY, u"Debug", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.m_debug, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )


		bSizer2.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_closeBtn = wx.Button( self, wx.ID_CANCEL, u"Close dialog", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.m_closeBtn, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )


		bSizer1.Add( bSizer2, 0, wx.EXPAND, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass



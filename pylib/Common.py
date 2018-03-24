import os
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QImage, QPixmap
import DbQuery

def find_image( system_path, table_name, unique_id ):
    extensions = [ 'jpg', 'jpeg', 'gif', 'png', ]
    #base_path_name = os.path.join( THIS_DIR, '{}/portraits/{}/{}'.format( system_path, table_name, unique_id ) )
    base_path_name = os.path.join( system_path, 'portraits/{}/{}'.format( table_name, unique_id ) )
    for ext in extensions:
        full_name = '{}.{}'.format( base_path_name, ext )
        if os.path.isfile( full_name ):
            return full_name

    for ext in extensions:
        #default_image = os.path.join( THIS_DIR, '{}/portraits/default.{}'.format( system_path, ext ) )
        default_image = os.path.join( system_path, 'portraits/default.{}'.format( ext ) )
        if os.path.isfile( default_image ):
            return default_image

    system_parent = os.path.abspath( os.path.join( system_path, os.pardir ) )
    base_dir = os.path.abspath( os.path.join( system_parent, os.pardir ) )
    return os.path.join( base_dir, 'images/noImage.jpg' )

def get_pixmap_from_base64( base64 ):
    byte_array = QtCore.QByteArray.fromBase64( base64.encode() )
    image = QImage.fromData( byte_array )
    pixmap = QPixmap( image )
    if pixmap.height() > 200 or pixmap.width() > 200:
        pixmap = pixmap.scaled( 200, 200, QtCore.Qt.KeepAspectRatio )
    return pixmap

def callback_factory( callback, *args, **kwargs ):
    return lambda: callback( *args, **kwargs )

def add_item_to_listbox( listbox, item, tool_tip=None, fields=None, original_list=None, wizard=None ):
    if type( item ).__name__ == 'str':
        list_item = QListWidgetItem()
        list_item.setText( item )
        if original_list:
            list_item.original_list = original_list
        listbox.addItem( list_item )
    elif type( item ).__name__ == 'dict':
        item_dict = item
        table_name = item['TableName']
        display_col = DbQuery.getDisplayCol( table_name )
        display = item[ display_col ]
        list_item = QListWidgetItem()
        list_item.setText( display )
        list_item.setData( QtCore.Qt.UserRole, item )
        if original_list:
            list_item.original_list = original_list
        listbox.addItem( list_item )
    elif type( item ).__name__ == 'tuple':
        display = item[0]
        item_dict = item[1]
        list_item = QListWidgetItem()
        list_item.setText( display )
        list_item.setData( QtCore.Qt.UserRole, item_dict )
        if original_list:
            list_item.original_list = original_list
        listbox.addItem( list_item )

    if tool_tip:
        if wizard:
            tool_tip_return = tool_tip( item_dict, fields, wizard.wizard_pages, wizard.external_data )
        else:
            tool_tip_return = tool_tip( item_dict, fields )
        list_item.setToolTip( tool_tip_return )

def fill_listbox( listbox, fill, tool_tip=None, fields=None, original_list=None, wizard=None ):
    listbox.clear()
    for item in fill:
        add_item_to_listbox( listbox, item, tool_tip, fields, original_list, wizard )

import inspect
import sqlite3
import Db
import DbDefs
import DbLayout

DB = None
SCHEMA_QUERY = 'SELECT sql FROM sqlite_master WHERE type = "table" and name = ?'

def initDB( path ):
    global DB
    DB = sqlite3.connect( path )
    DB.row_factory = dict_factory

def dict_factory( cursor, row ):
    d = {}
    for i, col in enumerate( cursor.description ):
        d[ col[0] ] = row[i]
    return d

def remove_single_quotes( string ):
    if string[0] == "'" and string[-1] == "'":
        return string[1:-1]
    return string

def parse_schema( schema, marker=None ):
    defs = schema[ schema.find( '(' ) + 1 : -1 ].split( ',' )
    if marker is None:
        cols = []
        for definition in defs:
            def_split = definition.split()
            def_split[0] = remove_single_quotes( def_split[0] )
            cols.append( def_split )
        return cols

    for definition in defs:
        if marker in definition:
            return remove_single_quotes( definition.split()[0] )

def getSchema( table_name ):
    cursor = DB.cursor()
    cursor.execute( SCHEMA_QUERY, ( table_name, ) )
    return cursor.fetchone()['sql']

def getTable( table_name ):
    meta_table_name = None
    for meta_map in DbLayout.db_meta_map:
        if table_name == meta_map[0]:
            meta_table_name = meta_map[1]
            break
    table = []
    cursor = DB.cursor()
    cursor.execute( 'SELECT * FROM {}'.format( table_name ) )
    rows = cursor.fetchall()
    if meta_table_name:
        schemas = cursor.execute( SCHEMA_QUERY, ( table_name, ) )
        schema = schemas.fetchone()['sql']
        meta_schemas = cursor.execute( SCHEMA_QUERY, ( meta_table_name, ) )
        meta_schema = meta_schemas.fetchone()['sql']
        #print( schema )
        #print( meta_schema )
        unique_col = parse_schema( schema, 'UNIQUE' )
        reference_col = parse_schema( meta_schema, 'REFERENCES' )
        #print( unique_col )
        #print( reference_col )
        for row in rows:
            cursor.execute( 'SELECT * FROM {} WHERE {}=?'.format( meta_table_name, reference_col ), ( row[ unique_col ], ) )
            row[ meta_table_name ] = cursor.fetchall()
    for row in rows:
        row['TableName'] = table_name
    return rows

def getCols( table_name ):
    cursor = DB.cursor()
    cursor.execute( SCHEMA_QUERY, ( table_name, ) )
    schema = cursor.fetchone()['sql']
    return parse_schema( schema )

def getDisplayCol( table_name ):
    db_dict = Db.__dict__
    for k,v in db_dict.items():
        if inspect.isclass( v ) and issubclass( v, DbDefs.Table ) and v.table_name == table_name:
            return v.cols[ v.display_col ]


def get_display(record):
    return record[getDisplayCol(record['TableName'])]


def getBase64Col( table_name ):
    db_dict = Db.__dict__
    for k,v in db_dict.items():
        if inspect.isclass( v ) and issubclass( v, DbDefs.Table ) and v.table_name == table_name:
            base64_col = v.base64_image_col
            if base64_col is not None:
                return v.cols[ base64_col ]

def make_def_string( table ):
    def_string = ''
    cols = table.cols
    colDefs = table.colDefs
    for i, col in enumerate( cols ):
        def_string += "'{}' {}".format( col, colDefs[i] )
        if i < len( cols ) - 1:
            def_string += ', '

    return def_string

def make_values_string( row ):
    values_string = ''
    for i, value in enumerate( row ):
        value = value.replace( "'", "''" )
        values_string += "'{}'".format( value )
        if i < len( row ) - 1:
            values_string += ', '
    return values_string

def resetDB():
    cursor = DB.cursor()
    db_dict = Db.__dict__
    for k,v in db_dict.items():
        if inspect.isclass( v ) and issubclass( v, DbDefs.Table ) and v.table_name != DbDefs.Table.table_name:
            print( v.table_name )
            cursor.execute( 'DROP TABLE IF EXISTS {}'.format( v.table_name ) )
            #print( make_def_string( v ) )
            cursor.execute( 'CREATE TABLE {} ({})'.format( v.table_name, make_def_string( v )  ) )
            for row in v.data:
                #print( make_values_string( row ) )
                cursor.execute( 'INSERT INTO {} VALUES ({})'.format( v.table_name, make_values_string( row ) ) )

    DB.commit()

def begin():
    pass

def commit():
    DB.commit()

def updateRow( table_name, where_col, where, row ):
    cursor = DB.cursor()
    update_string = 'UPDATE {} SET '.format( table_name )
    cols = [ col[0] for col in getCols( table_name ) ]
    for i, col in enumerate( cols):
        update_string += '{} = ?'.format( col )
        if i < len( cols ) - 1:
            update_string += ', '
    update_string += ' WHERE {} = "{}"'.format( where_col, where )
    values = tuple( val for val in row )
    try:
        cursor.execute( update_string, values )
        return True
    except sqlite3.Error:
        return False

def deleteRow( table_name, where_col, where ):
    cursor = DB.cursor()
    delete_string = 'DELETE FROM {} WHERE {}="{}"'.format( table_name, where_col, where )
    try:
        cursor.execute( delete_string )
        return True
    except sqlite3.Error:
        return False

def insertRow( table_name, row ):
    cursor = DB.cursor()
    insert_string = 'INSERT INTO {} VALUES ('.format( table_name )
    for i in range( len( row ) ):
        insert_string += '?'
        if i  < len( row ) - 1:
            insert_string += ', '
    insert_string += ')'
    try:
        cursor.execute( insert_string, tuple( v for v in row ) )
        return cursor.lastrowid
    except sqlite3.Error as e:
        print( 'Error Inserting Row:', e )
        print( 'First Column Data:', row[0] )
        return -1

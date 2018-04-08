#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
This creates a Db.py file from a series of csv files in this specific format:
row 1: first cell holds the table name - all others are empty
row 2: a column name for each cell
row 3: a column definition for each cell
row 4: column metadata - primarily used to denote which column holds the display string and which colums hold image info
row 5 and up: actual table data

Note about line breaks:
Normal line breaks will cause the Db.py file to have corrupt data. Use \n for line breaks within a data cell instead of pressing enter/return.
Example: This is the first paragraph.\nThis is the second paragraph.

Also, the class names are derived from the csv filenames so don't name the files with a python reserved word. https://docs.python.org/release/2.5.4/ref/keywords.html
"""
import sys

class DbScript:
    tables = []
    outputString = ""

    def __init__(self, filenameList):
        self.outputString += "# -*- coding: utf-8 -*-\nfrom DbDefs import Table\n\n"
        for filename in filenameList:
            self.addCSV(filename)
        self.prepareOutputString()

    def addCSV(self, filename):
        self.tables.append(filename)

    def prepareOutputString(self):
        for table in self.tables:
            className = table.replace(".csv", "")
            self.outputString += "class " + className + "(Table):\n"

            lines = [line.strip() for line in open(table)]
            headers = lines[:4]
            data = lines[4:]
            tableName = headers[0].replace(",", "")
            cols = headers[1]
            colDefs = headers[2]
            colMetaList = headers[3].split(",")

            self.outputString += "    table_name = " + tableName + "\n"
            self.outputString += "    cols = [" + cols + "]\n"
            self.outputString += "    colDefs = [" + colDefs + "]\n"

            colCount = 0
            for colMeta in colMetaList:
                if colMeta != "":
                    metaName = colMeta.replace("'", "")
                    self.outputString += "    " + metaName + " = " + str(colCount) + "\n" 
                colCount += 1

            self.outputString += "    data = [\n"
            for datum in data:
                self.outputString += "        [" + self.sanitizeDatum(datum) + "],\n"
            self.outputString += "        ]\n\n"

    def sanitizeDatum(self, datum):
        while(datum.__contains__("''")):
            datum = datum.replace("''", "\\'")
        while(datum.__contains__("\\\\',")):
            datum = datum.replace("\\\\',", "\\'',")
        while(datum.__contains__(",,")):
            datum = datum.replace(",,",",'',")
        if(datum.endswith(",")):
            datum = datum + "''"

        #while(datum.__contains__("'''")):
        #    datum = datum.replace("'''","\\''")

        return datum

    def getOutputString(self):
        return self.outputString

    def createDbScript(self):
        outputFile = open("Db.py", 'w')
        outputFile.write(self.outputString)
        """print str(self.outputString)"""


if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)

    if argc < 2:
        print("usage: " + argv[0] + " csvfilelist")
        exit(1)

    dbScript = DbScript(argv[1:])
    dbScript.createDbScript()

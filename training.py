#!/usr/bin/python
""" Try to convert the Toastmasters training page into something tolerable """
from bs4 import BeautifulSoup
import sys, re, xlsxwriter
headers = "Div,Area,Club Name,Number,Status,Trained,Pres,VPE,VPM,VPPR,Sec,Treas,SAA"
sheets = {}
formats = {}
class mysheet:
    def __init__(self, outbook, divname):
        print 'creating sheet for division "%s"' % divname
        self.sheet = outbook.add_worksheet('Division ' + divname)
        self.sheet.write_row(0, 0, headers.split(','), formats['bold'])
        self.sheet.set_column('A:A', 3)
        self.sheet.set_column('B:B', 4)
        self.sheet.set_column('C:C', 35)
        self.sheet.set_column('D:D', 8, formats['right'])
        self.sheet.set_column('G:M', 4, formats['center'])
        self.row = 1
        sheets[divname] = self
        
    def addrow(self, row, format=None):
        self.sheet.write_row(self.row, 0, row, format)
        self.row += 1
    

def makediv(outfile, outbook, divname, curdiv):
    divname = divname
    mysheet(outbook, divname)
    if curdiv:
        outfile.write('</tbody>\n')
        outfile.write('</table>\n')
        outfile.write('</div>\n')
        outfile.write('<div class="page-break"></div>\n')
    outfile.write('<div id="training-div-%s" class="trainingdiv">\n' % divname)
    outfile.write('<table>')
    outfile.write('<colgroup>' +
              '<col span="1" style="width: 5%;">' + # /Division
              '<col span="1" style="width: 5%;">' + # /Area
              '<col span="1" style="width: 35%; ">' + # /Club Name
              '<col span="1" style="width: 9%;">' + # /Club Number
              '<col span="1" style="width: 6%;">' + # /Status
              '<col span="1" style="width: 5%;">' + # / Trained
              '<col span="1" style="width: 5%;">' + # / President
              '<col span="1" style="width: 5%;">' + # / VPE
              '<col span="1" style="width: 5%;">' + # / VPM
              '<col span="1" style="width: 5%;">' + # / VPPR
              '<col span="1" style="width: 5%;">' + # / Secretary
              '<col span="1" style="width: 5%;">' + # / Treasurer
              '<col span="1" style="width: 5%;">' + # / SAA
              '</colgroup>\n')
    outfile.write('<thead style="font-weight:bold";><tr><td>')
    outfile.write('</td><td>'.join(headers.split(',')))
    outfile.write('</td></tr></thead>\n')
    outfile.write('<tbody>')


finder = re.compile(r'.*AREA *([0-9]*) *DIVISION *([A-Za-z] *)')
results = []
soup = BeautifulSoup(open(sys.argv[1], 'r'))
# From what I see in the documentation, I should be able to use one select, but it fails, so I'll break it up.
thediv = soup.select('div[id*="DistrictTraining"]')[0]
mydiv = BeautifulSoup(repr(thediv))
tbl = mydiv.select('table tbody tr td table tbody')[-1]
# Now we just power through the rows.  If they have an Area/Division, use it.
for t in tbl:
    if t.name == 'tr':
        if 'class' in t.attrs:
            cname = unicode(t['class'][0])
            if cname in [u'even', u'odd']:
                parts = t.select('td')
                clubname = ''.join(parts[1].stripped_strings)
                clubstatus = ''.join(parts[3].stripped_strings)
                clubnumber = ''.join(parts[2].stripped_strings)
                row = [division, area, clubname, clubstatus, clubnumber]
                offlist = []
                trained = 0
                for o in t.select('input[type="checkbox"]'):
                    if 'checked' in o.attrs:
                        trained += 1
                        offlist.append('X')
                    else:
                        offlist.append(' ')
                row.append(trained)
                row.extend(offlist)
                results.append(row)                
        else:
            contents = ' '.join(t.stripped_strings)
            match = finder.match(contents)
            if match:
                area = match.group(1).strip()
                division = match.group(2).strip()

# Now, create the HTML result file and the matching Excel spreadsheet
results.sort()
print 'results is %d long' % len(results)
outfile = open('training.html', 'w')
outbook = xlsxwriter.Workbook('training.xlsx')
formats['bold'] =  outbook.add_format({'bold': True})
xbold = formats['bold']
formats['center'] = outbook.add_format()
formats['center'].set_align('center')
formats['right'] = outbook.add_format()
formats['right'].set_align('right')
xlucky = outbook.add_format()
xlucky.set_bg_color('#ADD8E6')
xdcp = outbook.add_format()
xdcp.set_bg_color('#90EE90')
xuntrained = outbook.add_format()
xuntrained.set_bg_color('#FF8E8E')
outfile.write("""<html><head><title>Training Status</title>
        <style type="text/css">
        body {font-family: "Myriad-Pro", Arial, sans serif}
        tr, td, th {border-collapse: collapse; border-width: 1px; border-color: black; border-style: solid;}
        table {margin-bottom: 24px; border-collapse: collapse; border-width: 1px; border-color: black; border-style: solid;}
        .firstarea {margin-top: 12px; border-width-top: 2px;}
        .lucky {background-color: lightblue}
        .dcp {background-color: lightgreen}
        .untrained {background-color: #FF8E8E}
        .trainingtable {border-color: black; border-spacing: 0;}
        .trainingtable thead {font-weight: bold;}
        .page-break {page-break-before: always !important; break-before: always !important; display: block; float: none; position: relative;}
        .clubnum {text-align: right; padding-right: 2px}
        .clubname {font-weight: bold;}
        .trained {text-align: right; padding-right: 2px}
        .tstat {text-align: center;}
        @media print { body {-webkit-print-color-adjust: exact !important;}}
       </style></head>""")
outfile.write("<body>")
curdiv = ''
curarea = ''

for row in results:
    if row[0] != curdiv:
        makediv(outfile, outbook, row[0], curdiv)
        curdiv = row[0]
    outfile.write('<tr')
    classes = []
    format = None
    if row[1] != curarea:
        classes.append('firstarea')
        curarea = row[1]
    if row[5] == 7:
        classes.append('lucky')
        format = xlucky
    elif row[5] >= 4:
        classes.append('dcp')
        format = xdcp
    elif row[5] == 0:
        classes.append('untrained')
        format = xuntrained
    if classes:
        outfile.write(' class="%s"' % ' '.join(classes))
    outfile.write('>\n')
    for partnum in xrange(len(row)):
        outfile.write('<td')
        if partnum == 2:
            outfile.write(' class="clubname"')
        elif partnum == 3:
            outfile.write(' class="clubnum"')
        elif partnum == 5:
            outfile.write(' class="trained"')
        elif partnum > 5:
            outfile.write(' class="tstat"')
        outfile.write('>%s</td>\n' % row[partnum])
    outfile.write('</tr>\n')
    sheets[curdiv].addrow(row, format)
        
outfile.write('</tbody>\n</table>\n</div>\n')
outfile.write('</body></html>\n')
outfile.close()
outbook.close()

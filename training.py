#!/usr/bin/python2.7
""" Try to convert the Toastmasters training page into something tolerable """
from bs4 import BeautifulSoup
import sys, re, xlsxwriter
headers = "Div,Area,Club Name,Number,Status,Trained,Pres,VPE,VPM,VPPR,Sec,Treas,SAA"
sheets = {}
colors = {}
colors['lucky'] = '#ADD8E6'
colors['dcp'] = '#90EE90'
colors['untrained'] = '#FF8E8E'


class mysheet:
    @classmethod
    def setup(self, outbook):
        # Create the format objects we're going to need
        self.align = 3*['left'] + ['right'] + ['left'] + ['right'] + 7*['center']

        self.formats = {}
        self.formats[''] = [outbook.add_format({'border':1, 'align': self.align[i]}) for i in xrange(len(self.align))]
        self.formats['lucky'] = [outbook.add_format({'border':1, 'align': self.align[i], 'bg_color': colors['lucky']}) for i in xrange(len(self.align))]
        self.formats['dcp'] = [outbook.add_format({'border':1, 'align': self.align[i], 'bg_color': colors['dcp']}) for i in xrange(len(self.align))]
        self.formats['untrained'] = [outbook.add_format({'border':1, 'align': self.align[i], 'bg_color': colors['untrained']}) for i in xrange(len(self.align))]
        self.formats['bold'] = [outbook.add_format({'border':1, 'align': self.align[i], 'bold': True}) for i in xrange(len(self.align))]
        print 'setup complete'

    def __init__(self, outbook, divname):
        self.sheet = outbook.add_worksheet('Division ' + divname)
        elements = headers.split(',')
        for i in xrange(len(elements)):
            self.sheet.write(0, i, elements[i], self.formats['bold'][i])
        self.sheet.set_column('A:A', 3)
        self.sheet.set_column('B:B', 4)
        self.sheet.set_column('C:C', 45)
        self.sheet.set_column('D:D', 8)
        self.sheet.set_column('G:M', 5)
        self.row = 1
        sheets[divname] = self
        
    def addrow(self, row, classes):
        if 'lucky' in classes:
            format = self.formats['lucky']
        elif 'dcp' in classes:
            format = self.formats['dcp']
        elif 'untrained' in classes:
            format = self.formats['untrained']
        else:
            format = self.formats['']
        for i in xrange(len(row)):
            self.sheet.write(self.row, i, row[i], format[i])
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
outfile = open('report.html', 'w')
outbook = xlsxwriter.Workbook('report.xlsx')
mysheet.setup(outbook)
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
    if row[1] != curarea:
        classes.append('firstarea')
        curarea = row[1]
    if row[5] == 7:
        classes.append('lucky')
    elif row[5] >= 4:
        classes.append('dcp')
    elif row[5] == 0:
        classes.append('untrained')
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
    sheets[curdiv].addrow(row, classes)
        
outfile.write('</tbody>\n</table>\n</div>\n')
outfile.write('</body></html>\n')
outfile.close()
outbook.close()

from Tkinter import *
from ttk import *
import tkFileDialog
import tkMessageBox
from math import *
import json
from urllib2 import *


def make_request(url):
    req = Request('http://www.thebluealliance.com' + url)
    req.add_header('X-TBA-App-Id', 'jlmcmchl:OPRCalc_2015:0.1')
    return json.loads(urlopen(req).read().decode(encoding='UTF-8'))


def matrices(teams, matches):
    opr_A = [[0]*len(teams) for _ in xrange(len(teams))]

    opr_b = [0]*len(teams)
    dpr_b = [0]*len(teams)

    for match in matches:
        r1 = teams.index(int(match['alliances']['red']['teams'][0][3:]))
        r2 = teams.index(int(match['alliances']['red']['teams'][1][3:]))
        r3 = teams.index(int(match['alliances']['red']['teams'][2][3:]))
        b1 = teams.index(int(match['alliances']['blue']['teams'][0][3:]))
        b2 = teams.index(int(match['alliances']['blue']['teams'][1][3:]))
        b3 = teams.index(int(match['alliances']['blue']['teams'][2][3:]))

        opr_A[r1][r1] += 1
        opr_A[r1][r2] += 1
        opr_A[r1][r3] += 1

        opr_A[r2][r1] += 1
        opr_A[r2][r2] += 1
        opr_A[r2][r3] += 1

        opr_A[r3][r1] += 1
        opr_A[r3][r2] += 1
        opr_A[r3][r3] += 1

        opr_A[b1][b1] += 1
        opr_A[b1][b2] += 1
        opr_A[b1][b3] += 1

        opr_A[b2][b1] += 1
        opr_A[b2][b2] += 1
        opr_A[b2][b3] += 1

        opr_A[b3][b1] += 1
        opr_A[b3][b2] += 1
        opr_A[b3][b3] += 1

        rs = match['alliances']['red']['score']
        bs = match['alliances']['blue']['score']
        opr_b[r1] += rs
        opr_b[r2] += rs
        opr_b[r3] += rs
        opr_b[b1] += bs
        opr_b[b2] += bs
        opr_b[b3] += bs

        dpr_b[r1] += bs
        dpr_b[r2] += bs
        dpr_b[r3] += bs
        dpr_b[b1] += rs
        dpr_b[b2] += rs
        dpr_b[b3] += rs

    return getL(opr_A), opr_b, dpr_b


def totals(ranks):
    return zip(*ranks[1:])[3:8]


def getL(m):
    final = [[0.0]*len(m) for _ in xrange(len(m))]
    for i in xrange(len(m)):
        for j in xrange(i+1):
            final[i][j] = m[i][j] - sum(final[i][k] * final[j][k] for k in xrange(j))
            if i == j:
                final[i][j] = sqrt(final[i][j])
            else:
                final[i][j] /= final[j][j]
    return final


def forwardSubstitute(m,n):
    final = list(n)
    for i in xrange(len(m)):
        final[i] -= sum(m[i][j]*final[j] for j in xrange(i))
        final[i] /= m[i][i]
    return final


def backSubstitute(m,n):
    final = list(n)
    l = xrange(len(m)-1, -1, -1)
    for i in l:
        final[i] -= sum(m[i][j]*final[j] for j in xrange(i+1,len(m)))
        final[i] /= m[i][i]
    return final


def transpose(arr):
    return [[arr[y][x] for y in xrange(len(arr))] for x in xrange(len(arr[0]))]


def cholesky(L,b):
    y = forwardSubstitute(L, b)
    return backSubstitute(transpose(L), y)


class EventWindow(object):
    event_codes = [
        ['Alamo', 'txsa'], ['Arizona East', 'azch'], ['Arizona West', 'azpx'], ['Arkansas Rock City', 'arfa'],
        ['Auburn', 'waahs'], ['Auburn Mountainview', 'waamv'], ['Australia', 'ausy'], ['Bayou', 'lake'],
        ['Bedford', 'mibed'], ['Bridgewater-Raritan', 'njbri'], ['Buckeye', 'ohcl'], ['Center Line', 'micen'],
        ['Central Illinois', 'ilil'], ['Central Valley', 'cama'], ['Central Washington University', 'waell'],
        ['Chesapeake', 'mdcp'], ['Colorado', 'code'], ['Dallas', 'txda'], ['Escanaba', 'miesc'],
        ['FIRST in Michigan', 'micmp'], ['Festival de Robotique - Montreal', 'qcmo'], ['Finger Lakes', 'nyro'],
        ['Georgia Southern Classic', 'gape'], ['Glacier Peak', 'wasno'], ['Granite State', 'nhnas'],
        ['Great Lakes Bay Region', 'mimid'], ['Greater DC', 'dcwa'], ['Greater Kansas City', 'mokc'],
        ['Greater Pittsburgh', 'papi'], ['Greater Toronto Central', 'onto2'], ['Greater Toronto East', 'onto'],
        ['Gull Lake', 'migul'], ['Hartford', 'cthar'], ['Hatboro-Horsham', 'pahat'], ['Hawaii', 'hiho'],
        ['Howell', 'mihow'], ['Hub City', 'txlu'], ['Indiana FIRST', 'incmp'], ['Indianapolis', 'inind'],
        ['Inland Empire', 'carm'], ['Israel', 'ista'], ['Kentwood', 'miken'], ['Kettering University', 'miket'],
        ['Kokomo City of Firsts', 'inkok'], ['Lake Superior', 'mndu'], ['Lansing', 'milan'], ['Las Vegas', 'nvlv'],
        ['Livonia', 'miliv'], ['Lone Star', 'txho'], ['Los Angeles', 'calb'], ['Mexico City', 'mxmc'],
        ['Mid-Atlantic Robotics', 'mrcmp'], ['Midwest', 'ilch'], ['Minnesota 10000 Lakes', 'mnmi'],
        ['Minnesota North Star', 'mnmi2'], ['Mount Vernon', 'wamou'], ['Mt. Olive', 'njfla'], ['NE FIRST', 'necmp'],
        ['New York City', 'nyny'], ['New York Tech Valley', 'nytr'], ['North Bay', 'onnb'],
        ['North Brunswick', 'njnbr'], ['North Carolina', 'ncre'], ['Northeastern University', 'mabos'],
        ['Northern Lights', 'mndu2'], ['Oklahoma', 'okok'], ['Oregon City', 'orore'], ['Orlando', 'flor'],
        ['Pacific Northwest', 'pncmp'], ['Palmetto', 'scmb'], ['Peachtree', 'gadu'], ['Philomath', 'orphi'],
        ['Pine Tree', 'melew'], ['Pioneer Valley', 'maspr'], ['Purdue', 'inwla'], ['Queen City', 'ohci'],
        ['Reading', 'marea'], ['Rhode Island', 'rismi'], ['SBPLI Long Island', 'nyli'], ['Sacramento', 'casa'],
        ['San Diego', 'casd'], ['Seneca', 'njtab'], ['Shorewood', 'washo'], ['Silicon Valley', 'casj'],
        ['Smoky Mountains', 'tnkn'], ['South Florida', 'flfo'], ['Southfield', 'misou'],
        ['Springside Chestnut Hill', 'paphi'], ['St. Joseph', 'misjo'], ['St. Louis', 'mosl'], ['Standish', 'mista'],
        ['Suffield Shakedown', 'ctss'], ['Traverse City', 'mitvc'], ['Troy', 'mitry'], ['UMass - Dartmouth', 'manda'],
        ['UNH', 'nhdur'], ['Upper Darby', 'padre'], ['Utah', 'utwv'], ['Ventura', 'cave'], ['Virginia', 'vari'],
        ['Waterbury', 'ctwat'], ['Waterford', 'miwat'], ['Waterloo', 'onwa'], ['Week Zero', 'nhwz'],
        ['West Michigan', 'miwmi'], ['West Valley', 'waspo'], ['Western Canada', 'abca'], ['Wilsonville', 'orwil'],
        ['Windsor Essex Great Lakes', 'onwi'], ['Wisconsin', 'wimi'], ['Woodhaven', 'mifla']]

    def __init__(self, root):
        top = Toplevel(root)
        top.title('Events')

        event = (('nm', 'Name', 200, 'w'),
                 ('cd', 'Code', 50, 'w'))

        self.__tvEvent = Treeview(top, columns=[r[0] for r in event], show='headings')
        for r, h, w, s in event:
            self.__tvEvent.column(r, width=w, anchor=s)
            self.__tvEvent.heading(r, text=h)

        for event in EventWindow.event_codes:
            self.__tvEvent.insert('', 'end', values=event)

        s = Scrollbar(top)
        s.pack(side=RIGHT, fill=Y)
        s.config(command=self.__tvEvent.yview)
        self.__tvEvent.config(yscrollcommand=s.set)
        self.__tvEvent.pack(fill=BOTH)


class Gui(object):
    def __init__(self, root):
        self.__root = root
        self.__ranks = []
        self.__matches = []
        self.__metrics = []
        self.__prs = []

        frame = Frame(root)
        frame.pack()
        self.__event = StringVar()

        self.__tabs = Notebook(frame)

        rank = self.__rank_header = (('rnk', 'Rank', 40),
                                     ('tm', 'Team', 40),
                                     ('avg', 'Qual Avg', 65),
                                     ('auto', 'Auto', 50),
                                     ('cont', 'Container', 75),
                                     ('coop', 'Coopertition', 80),
                                     ('lit', 'Litter', 50),
                                     ('tote', 'Tote', 50),
                                     ('play', 'Played', 50))
        match = self.__match_header = (('m#', 'Match', 50),
                                       ('r1', 'Red 1', 50),
                                       ('r2', 'Red 2', 50),
                                       ('r3', 'Red 3', 50),
                                       ('b1', 'Blue 1', 50),
                                       ('b2', 'Blue 2', 50),
                                       ('b3', 'Blue 3', 50),
                                       ('rs', 'Red Score', 75),
                                       ('be', 'Blue Score', 75))
        prs = self.__prs_header = (('tm', 'Team', 50),
                                   ('opr', 'OPR', 50),
                                   ('apr', 'Auto', 50),
                                   ('c1pr', 'Container', 75),
                                   ('c2pr', 'Coopertition', 75),
                                   ('lpr', 'Litter', 50),
                                   ('tpr', 'Tote', 50),
                                   ('fpr', 'Foul', 50),
                                   ('dpr', 'DPR', 50))

        rankFrame = Frame(self.__tabs)
        matchFrame = Frame(self.__tabs)
        oprFrame = Frame(self.__tabs)

        self.__trRank = Treeview(rankFrame, columns=[r[0] for r in rank], show='headings')
        self.__trMatch = Treeview(matchFrame, columns=[r[0] for r in match], show='headings')
        self.__trOPR = Treeview(oprFrame, columns=[r[0] for r in prs], show='headings')

        for r, h, w in rank:
            self.__trRank.column(r, width=w, anchor='e')
            self.__trRank.heading(r, text=h)
        for r, h, w in match:
            self.__trMatch.column(r, width=w, anchor='e')
            self.__trMatch.heading(r, text=h)
        for r, h, w in prs:
            self.__trOPR.column(r, width=w, anchor='e')
            self.__trOPR.heading(r, text=h)

        self.__tabs.add(rankFrame, text='Rankings')
        self.__tabs.add(matchFrame, text='Matches')
        self.__tabs.add(oprFrame, text='OPR')

        self.__trRank.pack()
        self.__trMatch.pack()
        self.__trOPR.pack()

        self.__tabs.grid(row=1, column=0)

        controls = Frame(frame)
        controls.grid(row=0, column=0, sticky=W+E)

        self.__enEvent = Entry(controls, textvariable=self.__event, width=10)
        self.__info = Label(controls, text='?', underline=0)
        self.__btnSave = Button(controls, text='Save Current Tab', command=self.save)

        self.__enEvent.bind('<Return>', self.get_event_data_wrapper)
        self.__info.bind("<Button-1>", lambda e: EventWindow(self.__root))

        self.__enEvent.pack(side=LEFT)
        self.__info.pack(side=LEFT)
        self.__btnSave.pack(side=RIGHT, fill=BOTH)

    def get_event_data_wrapper(self, *args):
        self.get_event_data()
        self.calc_oprs()

    def get_event_data(self):
        try:
            self.__ranks = make_request('/api/v2/event/2015%s/rankings' % self.__event.get().lower())
            self.__matches = make_request('/api/v2/event/2015%s/matches' % self.__event.get().lower())
        except StandardError:
            tkMessageBox.showerror('Data Unavailable',
                                   '\'%s\' does not have ranking/match data available on TBA.\n'
                                   'Check against the \'?\' for the list of events available through TBA.' %
                                   self.__event.get())
        self.__matches = [match for match in self.__matches if match['comp_level'] == 'qm']
        self.__matches.sort(lambda a, b: a['match_number'] - b['match_number'])

        self.load_raw()
        kids = self.__trOPR.get_children()
        if len(kids) > 0:
            for kid in kids:
                self.__trOPR.delete(kid)

        self.__tabs.select(0)

    def load_raw(self):
        for rank in self.__ranks[1:]:
            self.__trRank.insert('', 'end', values=rank)

        def raw(m):
            redTeams = m['alliances']['red']['teams']
            blueTeams = m['alliances']['blue']['teams']
            return (match['match_number'],
                    redTeams[0][3:],
                    redTeams[1][3:],
                    redTeams[2][3:],
                    blueTeams[0][3:],
                    blueTeams[1][3:],
                    blueTeams[2][3:],
                    m['alliances']['red']['score'],
                    m['alliances']['blue']['score'])

        for match in self.__matches:
            self.__trMatch.insert('', 'end', values=raw(match))


    def calc_oprs(self):
        teams = list(rank[1] for rank in self.__ranks[1:])
        opr_L, opr_b, dpr_b = matrices(teams, self.__matches)
        apr_b, c1pr_b, c2pr_b, lpr_b, tpr_b = zip(*self.__ranks[1:])[3:8]

        opr_x = cholesky(opr_L, opr_b)
        apr_x = cholesky(opr_L, apr_b)
        c1pr_x = cholesky(opr_L, c1pr_b)
        c2pr_x = cholesky(opr_L, c2pr_b)
        lpr_x = cholesky(opr_L, lpr_b)
        tpr_x = cholesky(opr_L, tpr_b)
        dpr_x = cholesky(opr_L, dpr_b)

        fpr_x = [opr_x[i] - apr_x[i] - c1pr_x[i] - c2pr_x[i] - lpr_x[i] - tpr_x[i] for i in xrange(len(opr_x))]

        self.__metrics = [[teams[i], opr_x[i], apr_x[i], c1pr_x[i], c2pr_x[i], lpr_x[i],
                          tpr_x[i], fpr_x[i], dpr_x[i]] for i in xrange(len(teams))]

        self.load_prs()

        self.__tabs.select(2)

    def load_prs(self):
        def fn(val):
            if val is not str:
                if int(val) != val:
                    val = round(val, 2)
                return str(val)
            return val

        for row in self.__metrics:
            self.__trOPR.insert('', 'end', values=[fn(v) for v in row])

    def save(self):
        options = dict()
        options['defaultextension'] = '.csv'
        options['filetypes'] = (('Comma Separated Values', '.csv'),
                                ('All Files', '.*'))

        name = tkFileDialog.asksaveasfilename(**options)

        if name != '':
            with open(name, 'w') as f:
                if self.__tabs.index(self.__tabs.select()) == 0:
                    f.write('\n'.join(','.join(map(str, row)) for row in self.__ranks))
                elif self.__tabs.index(self.__tabs.select()) == 1:
                    def raw(m):
                        redTeams = m['alliances']['red']['teams']
                        blueTeams = m['alliances']['blue']['teams']
                        return (m['match_number'],
                                redTeams[0][3:],
                                redTeams[1][3:],
                                redTeams[2][3:],
                                blueTeams[0][3:],
                                blueTeams[1][3:],
                                blueTeams[2][3:],
                                m['alliances']['red']['score'],
                                m['alliances']['blue']['score'])

                    f.write(','.join(h[1] for h in self.__match_header) + '\n')
                    f.write('\n'.join(','.join(map(str, raw(row))) for row in self.__matches))
                else:
                    f.write(','.join(h[1] for h in self.__prs_header) + '\n')
                    f.write('\n'.join(','.join(map(str, row)) for row in self.__metrics))

def main():
    root = Tk()
    root.title('Event OPR Calculator')
    Gui(root)
    root.mainloop()


if __name__ == '__main__':
    main()
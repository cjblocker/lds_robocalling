from datetime import datetime, timedelta
from numpy.random import randn
from .log import logging, log_call

from .database import Database, DATE_FORMAT
from .phone_api import Phone
from .email_api import EmailClient

SATURDAY = 5
GROUP_SIZE = 6

_logger = logging.getLogger('lds_cleanup.scheduler')

def month_str2int(month):
    if isinstance(month, str):
        month = month.strip()[:3].lower()
        month = {
            'jan': 1,
            'feb': 2,
            'mar': 3,
            'apr': 4,
            'may': 5,
            'jun': 6,
            'jul': 7,
            'aug': 8,
            'sep': 9,
            'oct':10,
            'nov':11,
            'dec':12
        }[month]
    elif month is None:
        month = 1
    return month    

def get_saturdays_in(month):

    now = datetime.now()
    if now.month <= month:
        year = now.year
    else:
        year = now.year + 1

    first_day = datetime(year,month,1);
    first_sat = first_day + timedelta(days=((SATURDAY - first_day.weekday()) % 7 ))
    sats = [first_sat];
    for sat in sats:
        s = sat + timedelta(days=7)
        if s.month != month:
            break
        else:
            sats.append(s)

    return sats

def compute_member_score(mem, month):
    score = min([mem['base_score'],1])*10
    score += .5*randn()
    if mem.get('days_helped'):
        last_helped = max(mem['days_helped'])
        month_last_helped = datetime.strptime(last_helped, "%Y-%m-%d").month 
        if month_last_helped > month:
            month = month + 12;
        diff = (month - month_last_helped)/2
        score -= (6-min([diff*(1.1**(len(mem['days_helped'])-1)), 6]))
    return max([score, 0])

def get_scored_members(db=None):
    if db is None:
        db = Database()
    members = db.get_scheduled_members('')
    for mem in members.values():
        mem['score'] = compute_member_score(mem,month)
    sch = sorted(members.values(), key=lambda mem:mem['score'], reverse=True)
    for mem in sch:
        _logger.debug("          |{ID: >12}: {name: <15} {surname: <15}, {base_score} => {score:2.3f}\n".format(**mem))
    return sch

@log_call(_logger)
def schedule(month):

    month = month_str2int(month)
    weeks = get_saturdays_in(month)
    db = Database()
    
    sch = get_scored_members(db)
    people_needed = GROUP_SIZE*len(weeks)
    sch = sch[:people_needed]

    for week in weeks:
        log = 'Scheduled {:%Y-%m-%d}:\n   ----------------------------------------\n'.format(week)
        group = sch[:GROUP_SIZE]
        sch = sch[GROUP_SIZE:]

        for mem in group:
            log += "   |{ID: >12}: {name: <15} {surname: <15}, {base_score} => {score:2.3f}\n".format(**mem)
            db.save_member({'ID':mem['ID'],'scheduled':DATE_FORMAT.format(week)})
        _logger.info(log)

    assert not sch 

def ord_ext(n):
    return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))

def notify_member(member, week, other_weeks=None):
    if other_weeks:
        wks = " ("
        for wk in other_weeks:
            wks += ord_ext(wk.day)
            wks += r'/'
        wks = wks[:-1] + ')'
    else:
        wks = ''


    message = """Hi {name}, 

I'm the Ann Arbor YSA building coordinator and I'm making building cleanup assignments for {week:%B} 
 and was wondering if you would be able to help on Saturday the {day} at 10am. 
 If not, would you be available any other Saturday in {week:%B}{wks}?"""
    message = message.format(name=member['name'],week=week, day=ord_ext(week.day),wks=wks)
    
    if member['sms_pref']:
        phn = Phone()
        phn.text(message.replace('\n',''), to=member['phone'])

    if member['email_pref']:
        emc = EmailClient()
        emc.send_email("Ann Arbor YSA Building Cleanup", body=message, to=member['email'])

def ischedule(month, pool=None):
    month = month_str2int(month)
    weeks = get_saturdays_in(month)
    for i in range(len(weeks)):
        print("{}: ".format(i) + DATE_FORMAT.format(weeks[i]))
    idx = input("Choose Week")
    week = weeks[idx]

    db = Database()
    if pool is None:
        pool = get_scored_members(db)

    for mem in pool:
        c = input("Assign {ID: >12}: {name: <15} {surname: <15}, {score:2.3f}, txt:{sms_pref}, e:{email_pref}?".format(**mem)).lower()
        if c == 'exit':
            return
        if c == 'next':
            week = weeks[idx+1]

        if c[0] == 'n' and c != 'next':
            pass
        else:
            notify_member(mem, week, weeks)
            db.save_member({'ID':mem['ID'], 'scheduled':'*'})



def main(month=None):
    if month is None:
        month = datetime.now().month
        if month % 2 == 0:
            month += 1
    schedule(month)

if __name__ == '__main__':
    main()

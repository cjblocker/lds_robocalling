from datetime import datetime, timedelta
from numpy.random import randn
from log import logging, log_call

from database import Database, DATE_FORMAT

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


@log_call(_logger)
def schedule(month):

    month = month_str2int(month)
    weeks = get_saturdays_in(month)
    db = Database()
    members = db.get_scheduled_members('')
    for mem in members.values():
        mem['score'] = compute_member_score(mem,month)
    sch = sorted(members.values(), key=lambda mem:mem['score'], reverse=True)
    for mem in sch:
        _logger.debug("          |{ID: >12}: {name: <15} {surname: <15}, {base_score} => {score:2.3f}\n".format(**mem))

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


if __name__ == '__main__':
    month = datetime.now().month
    if month % 2 == 0:
        month += 1

    schedule(month)

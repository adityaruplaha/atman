import datetime


class SchedClass:
    r"""
    Structure of a typical SchedClass string:

        2020-11-04_phy2_ad1
        \________/ \_/^ \_/
         ISO date   | |  |
                    | |  \_ class modifier   = 'ad1'   --> additional class 1 
                    | \____ subject modifier = int(2)  --> second course
                    \______ subject          = 'phy'   --> physics

    Class modifiers are OPTIONAL.
    """

    def __init__(self, sched_class):
        L = sched_class.split('_')
        self.date = datetime.date.fromisoformat(L[0])
        self.subject = L[1].strip('1234567890')
        self.subject_modifier = int(L[1][len(self.subject):])
        if L[2:]:
            self.class_identifier = L[2]
        else:
            self.class_identifier = None

    def __toString__(self):
        return '_'.join([
            self.date.isoformat(), self.subject + self.subject_modifier, self.class_identifier
        ])

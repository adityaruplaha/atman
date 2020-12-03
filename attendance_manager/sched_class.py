import datetime


class SchedClass:
    r"""
    Structure of a typical SchedClass class_id:

        2020-11-04_phy2_ad1
        \________/ \_/^ \_/
         ISO date   | |  |
                    | |  \_ class identifier = 'ad1'   --> additional class 1 
                    | \____ subject modifier = int(2)  --> second course
                    \______ subject          = 'phy'   --> physics

    Subject modifiers and class identifiers are OPTIONAL.
    """

    def __init__(self, class_id):
        L = class_id.split('_')
        self.date = datetime.date.fromisoformat(L[0])
        self.subject = L[1].strip('1234567890')
        self.subject_modifier = int(
            L[1][len(self.subject):]) if L[1][len(self.subject):] else None
        if L[2:]:
            self.class_identifier = L[2]
        else:
            self.class_identifier = None

    def __toString__(self):
        return '_'.join([
            self.date.isoformat(), self.subject +
            str(self.subject_modifier
                if self.subject_modifier != None
                else ''),
            (self.class_identifier
                if self.class_identifier != None
                else '')
        ])

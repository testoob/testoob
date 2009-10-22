import sys
import optparse
import getpass
import sqlite3

import gdata.projecthosting.client
import gdata.projecthosting.data
import gdata.gauth
import gdata.client
import gdata.data
import atom.http_core
import atom.core

CLIENT_NAME = "testoob_googlecode_issues"

def die(msg):
    print >>sys.stderr, msg
    sys.exit(1)

def get_optparser():
    p = optparse.OptionParser()
    p.add_option("--user", "-u", metavar="USERNAME")
    p.add_option("--project", "-p")
    p.add_option("--tracdb", metavar="FILE")
    p.add_option("--list", "-l", action="store_true", default=False)
    return p

def get_issues_client(username):
    password = getpass.getpass("Password for user '%s': " % username)

    issues_client = gdata.projecthosting.client.ProjectHostingClient()

    try:
        issues_client.client_login(username, password, CLIENT_NAME)
    except gdata.client.BadAuthentication, e:
        die("Couldn't authenticate user '%s': %s" % (username, e))

    return issues_client

class Issue:
    def __init__(self, trac_dict, google_code_dict, comments):
        self.trac_dict = trac_dict
        self.google_code_dict = google_code_dict
        self.comments = comments

def comment_trac2gcode(trac_dict):
    return {
        "comment": trac_dict["newvalue"] + "\n\n[originally commented on trac by %s]"%mangle_email(trac_dict["author"])
    }
class Comment:
    def __init__(self, trac_dict):
        self.trac_dict = trac_dict
        self.google_code_dict = comment_trac2gcode(trac_dict)

def mangle_email(email):
    return " xxATxx ".join(email.split("@")).replace(".", " dot ")
def convert_trac_ticket_row(row):
    def calc_content(trac_description, trac_reporter):
        return trac_description + "\n\n[originally reported on trac by %s]"%mangle_email(trac_reporter)
    def calc_status(trac_status, trac_resolution):
        if trac_status == "reopened":
            return "New"
        if trac_status != "closed":
            return trac_status.capitalize()

        # ticket is closed
        return trac_resolution.capitalize()

    def calc_labels(trac_type, trac_priority, trac_component, trac_milestone):
        result = []
        result.append("Type-" + trac_type.capitalize())
        priorities_map = {"normal":"Medium", "high":"High", "low":"Low", "lowest":"Low"}
        result.append("Priority-" + priorities_map[trac_priority])
        result.append("Component-" + trac_component.capitalize())
        if trac_milestone:
            result.append("Milestone-" + trac_milestone.capitalize())
        return result

    google_code_dict = {
        "title" : row["summary"],
        "content": calc_content(row["description"], row["reporter"]),
        "status": calc_status(row["status"], row["resolution"]),
        "labels": calc_labels(row["type"], row["priority"], row["component"], row["milestone"]),
    }
    if row["cc"]:
        google_code_dict["ccs"] = row["cc"].split(","),

    return Issue(dict(row), google_code_dict, [])
    # summary -> title
    # description -> content
    # status -> status
    #   "new" -> "New"
    #   "assigned" -> "Assigned"
    #   "closed" -> Based on resolution
    #   "reopened" -> "New"
    # type -> label:
    #    "defect" -> "Type-Defect"
    #    "enhancement" -> "Type-Enhancement"
    #    "task" -> "Type-Task"
    # priority -> label:
    #    "normal" -> "Priority-Medium"
    #    "high" -> "Priority-High"
    #    "low -> "Priority-Low"
    #    "lowest" -> "Priority-Low"
    # component -> label:
    #    "foo" -> "Component-Foo"
    # reporter -> text in content: [reported in Trac by foo xxATxx example.org]
    # cc -> ccs (after split)
    # milestone -> Label
    #    "foo" -> "Milestone-Foo"
    # resolution -> status
    #    "duplicate" -> "Duplicate"
    #    "fixed" -> "Fixed"
    #    "invalid" -> "Invalid"
    #    "wontfix" -> "WontFix"

def load_trac_tickets(trac_db_filename):
    with sqlite3.connect(trac_db_filename) as conn:
        c = conn.cursor()
        c.row_factory = sqlite3.Row
        try:
            c.execute("select * from ticket")
            for ticket_row in c:
                yield convert_trac_ticket_row(ticket_row)
        finally:
            c.close()

def populate_issue_comments(trac_db_filename, issues):
    with sqlite3.connect(trac_db_filename) as conn:
        c = conn.cursor()
        c.row_factory = sqlite3.Row
        try:
            for i in issues:
                c.execute("select * from ticket_change where ticket = ?", (i.trac_dict["id"],))
                for ticket_change_row in c:
                    i.comments.append(Comment(dict(ticket_change_row)))
                
            c.execute("select * from ticket")
        finally:
            c.close()


def main(args):
    optparser = get_optparser()

    opts, args = optparser.parse_args()

    def verify_required_option(option):
        if getattr(opts,option) is None:
            optparser.error("Missing required option '%s'" % option)
    
    verify_required_option('project')
    verify_required_option('user')
    verify_required_option('tracdb')

    print "Loading Trac tickets..."
    issues = list(load_trac_tickets(opts.tracdb))
    populate_issue_comments(opts.tracdb, issues)
    if opts.list:
        import pprint
        pprint.pprint(list((i.google_code_dict, [x.google_code_dict for x in i.comments]) for i in issues if i.comments))
        sys.exit(0)

    client = get_issues_client(opts.user)
    issues_feed = client.get_issues(opts.project)
    for issue in issues_feed.entry:
        print issue.title.text

if __name__ == "__main__":
    main(sys.argv)

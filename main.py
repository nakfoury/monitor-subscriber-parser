import sys
import re
import csv

event_pattern = re.compile(r'\w{3,6}day \w{3,9} \d{1,2} \d{4}', re.MULTILINE | re.DOTALL)
header_pattern = re.compile(r'(\d\d:\d\d:\d\d:\d\d\d) Eventid:(\d*)')
handshake_pattern = re.compile(r'(.*) from ([\d\.\:]*) to ([\d\.\:]*)')
sequenceNumber_pattern = re.compile(r'Sequence Number: (0x[\w\d]*)')
informationElement_pattern = re.compile(r' *([ \w]*):\n.*Value: ([\w\d]*)')
QCI_pattern = re.compile(r'(QCI): (\d*)')
commandCode_pattern = re.compile(r'Command Code: (.*) \(')
messageType_pattern = re.compile(r'Message type: (.*) \(')
cause_pattern = re.compile(r'Cause: (.*) \(')
avpLine_pattern = re.compile(r'(?:\[[VM]\] ){1,2}(.*):(?: (.*))?')

TARGET_LIST = ['Timestamp', 'SequenceNumber', 'Message Type/Command Code', 'Cause', 'Protocol', 'Source', 'Destination',
               'AVP Information', 'IMSI', 'MSISDN', 'MOBILE EQUIPMENT IDENTITY', 'RADIO ACCESS TECH',
               'ACCESS POINT NAME', 'EPS BEARER ID', 'QCI']


def get_seq(event):
    match = re.search(sequenceNumber_pattern, event)
    if match:
        return [('SequenceNumber', match.group(1))]
    else:
        return [('SequenceNumber', 'N/A')]


def get_id(event):
    match = re.search(header_pattern, event)
    if match:
        return [('Timestamp', match.group(1)), ('Eventid:', match.group(2))]
    else:
        return [('Timestamp', 'N/A'), ('Eventid:', 'N/A')]


def get_avp_lines(event):
    avps = event.split('AVP Information:\n')[1]
    result = avps.split('\n')


    return 'AVP Information', avps


def get_messageType(event):
    match = re.search(messageType_pattern, event)
    if match:
        return 'Message Type/Command Code', match.group(1)
    else:
        return 'Message Type/Command Code', 'N/A'


def get_cause(event):
    match = re.search(cause_pattern, event)
    if match:
        return 'Cause', match.group(1)
    else:
        return 'Cause', 'N/A'


def get_commandCode(event):
    match = re.search(commandCode_pattern, event)
    if match:
        return 'Message Type/Command Code', match.group(1)
    else:
        return 'Message Type/Command Code', 'N/A'


def get_handshake(event):
    result = []
    match = re.search(handshake_pattern, event)

    mtype = ('Message Type/Command Code', 'N/A')
    cause = ('Cause', 'N/A')
    pro = ('Protocol', 'N/A')
    src = ('Source', 'N/A')
    dest = ('Destination', 'N/A')
    avps = ('AVP Information', 'N/A')

    if match:
        src = ('Source', match.group(2))
        dest = ('Destination', match.group(3))

        if 'Diameter' in match.group(0):
            pro = ('Protocol', 'Diameter')
            # otherstuff (get AVP lines)
            avps = get_avp_lines(event)
            mtype = get_commandCode(event)

        elif 'GTPv2C' in match.group(0):
            pro = ('Protocol', 'GTPv2C')
            # otherstuff
            mtype = get_messageType(event)
            cause = get_cause(event)


        else:
            pro = ('Protocol', 'N/A')
    result.append(mtype)
    result.append(cause)
    result.append(pro)
    result.append(src)
    result.append(dest)
    result.append(avps)
    return result


def parse_event(event):
    result = []

    id = get_id(event)
    seq = get_seq(event)
    handshake = get_handshake(event)
    info = re.findall(informationElement_pattern, event)
    qci = re.findall(QCI_pattern, event)

    result += id
    result += seq
    result += handshake
    result += info
    result += qci

    return dict(result)  # dict


def print_results(data):
    # maybe later i'll add a pretty command line print fxn
    return


def output_csv(data):
    with open('./output.csv', 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=TARGET_LIST, extrasaction='ignore')
        writer.writeheader()
        i = 1
        for event in data:
            writer.writerow(event)
            print('parsing event {0} of {1}'.format(i, len(data)))
            i += 1
    return


def main():
    result = []
    print('i saw some args: {0}\n'.format(sys.argv))
    with open(sys.argv[1], 'r') as f:
        events = re.split(event_pattern, f.read())
    for event in events:
        parsed_event = parse_event(event)
        result.append(parsed_event)  # list of dicts
    output_csv(result)
    print('\nhooray! we made it. peep output.csv')


if __name__ == "__main__":
    main()

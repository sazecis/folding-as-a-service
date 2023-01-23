from xml.dom import minidom
import sys

if str(sys.argv[1]) == 'cpu_gpu':
    cpu_gpu = True
else:
    cpu_gpu = False

ip = str(sys.argv[2])

root = minidom.Document()

xml = root.createElement('config')
root.appendChild(xml)

fold_anon = root.createElement('fold-anon')
gpu = root.createElement('gpu')
allow = root.createElement('allow')
power = root.createElement('power')
user = root.createElement('user')
team = root.createElement('team')
web_allow = root.createElement('web-allow')
slot_cpu = root.createElement('slot')
if cpu_gpu:
    slot_gpu = root.createElement('slot')

fold_anon.setAttribute('v', 'true')
gpu.setAttribute('v', 'false')
power.setAttribute('v', 'full')
user.setAttribute('v', 'Anonymous')
team.setAttribute('v', '226715')
allow.setAttribute('v', ip)
web_allow.setAttribute('v', ip)
slot_cpu.setAttribute('id', '0')
slot_cpu.setAttribute('type', 'CPU')
if cpu_gpu:
    gpu.setAttribute('v', 'true')
    slot_gpu.setAttribute('id', '1')
    slot_gpu.setAttribute('type', 'GPU')

xml.appendChild(fold_anon)
xml.appendChild(gpu)
xml.appendChild(power)
xml.appendChild(user)
xml.appendChild(team)
xml.appendChild(allow)
xml.appendChild(web_allow)
xml.appendChild(slot_cpu)
if cpu_gpu:
    xml.appendChild(slot_gpu)

xml_str = root.toprettyxml(indent="\t")

save_path_file = "config_test.xml"

with open(save_path_file, "w") as f:
    f.write(xml_str)

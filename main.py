import re
import idzip
import lxml
from pyglossary import Glossary
from pyglossary.glossary_v2 import ConvertArgs, Glossary
from pypinyin.contrib.tone_convert import to_tone

def pinyin_to_tone(pinyin):
    if pinyin[-1:] == "1":
        return "1"
    elif pinyin[-1:] == "2":
        return "2"
    elif pinyin[-1:] == "3":
        return "3"
    elif pinyin[-1:] == "4":
        return "4"
    elif pinyin[-1:] == "5":
        return "5"
    else:
        return "6"

hanzi_regex = re.compile(r'(\S+)\s(\S+)\s\[([A-Z\-a-z12345,:·\s]+)\]\s/(.*)/')

def definition_split(definition):
    trad = hanzi_regex.search(definition).group(1)
    simp = hanzi_regex.search(definition).group(2)
    pinyin = hanzi_regex.search(definition).group(3)
    english = hanzi_regex.search(definition).group(4)

    chars = list(simp)
    tones = []
    for p in pinyin.split():
        tones.append(pinyin_to_tone(p))

    pinyin = format_pinyin(pinyin)
    org_chars = format_org_chars(chars, tones)
    meaning = format_meaning(english)
    # definition = [simp, org_chars, tones, pinyin, meaning]
    # definition = [simp, org_chars, pinyin, meaning]
    # definition = [simp, org_chars + "\t" + pinyin + "\n" + meaning + "\n"]
    definition = [simp, org_chars + "\t" + pinyin + "\n" + meaning]
    return definition
    
def format_pinyin(pinyin):
    words = ""
    for word in pinyin.split():
        word = word.replace("u:", "v")
        words += to_tone(word) + " "
    words = words[:-1]
    return words

def format_org_chars(chars, tones):
    org_chars = []
    for c, t in zip(chars, tones):
        if t == "6":
            org_chars += c
        else:
            org_chars += "[[t{}:][{}]]".format(pinyin_to_tone(t), c)
        org_chars = "".join(org_chars)
    return org_chars

def format_meaning(meaning):
    meaning = '\n'.join(meaning.split("/"))
    return meaning
    


"""Add words instead of pinyin from above"""
def cc_cedict_entry_to_stardict(entry):
    e = {(hanzi_regex.findall(entry)[0][1]): ''.join(org_chars) + "\t" + hanzi_regex.findall(test)[0][2] + "\n" + '\n'.join(hanzi_regex.findall(entry)[0][3].split("/"))}
    return e

# print(cc_cedict_entry_to_stardict(test))

cc_cedict_file = sys.argv[1]

mydict = {}
with open(cc_cedict_file,'r') as fin:
    # skip first 30 lines
    lines = fin.readlines()[30:]
# print(definition_split(lines[150]))
for line in lines:
    line = line.replace("\n", "")
    mydict.update(
        {definition_split(line)[0]:
         definition_split(line)[1]})
# #     # print(cc_cedict_entry_to_stardict(line))

home = os.path.expanduser('~')
stardict_dir = home + "/.local/share/stardict/dic/"
# stardict_dir = ""

Glossary.init()

glos = Glossary()

for word, defi in mydict.items():
	# glos.addEntryObj(glos.newEntry(
	glos.addEntry(glos.newEntry(
		word,
		defi,
		defiFormat="m",  # "m" for plain text, "h" for HTML
	))

glos.setInfo("title", "Org CC-Cedict")
glos.setInfo("author", "CC-Cedict contributers:\nConverted by Jiewawa")
# glos.write(stardict_dir + "org.ifo", format="Stardict", large_file=True)
glos.write(stardict_dir + "stardict-org-cc-cedict/"+ "org.ifo", format="Stardict", merge_syns=True)


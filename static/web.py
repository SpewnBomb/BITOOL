from flask import Flask, request, render_template, send_file
import jinja2
import re
import urllib

app = Flask(__name__)


var = "variable"
acession = ""
pattern = r'([^p])([^pkrhw])([vlswfnq])([iltywfn])([fiy])([^pkrh])'
errortext = ""


def validateinput(code):
    #make uppercase to avoid lazy user input
    code = code.upper()
    #check code is in accession code format
    if(re.fullmatch("[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}", code) is not None):
        validcode = code
        return validcode
    else:
        print("invalid acession code, try again")
        invalidcode = False
        return invalidcode

def getfasta(accessioncode , data, header):
    # build url
    if accessioncode == None:
        data = data.replace("\n", "")
        data = data.replace(" ", "")
        sequence = data
    #fetch fasta
    if data == None and header == None:
        url = "http://www.uniprot.org/uniprot/" + accessioncode + ".fasta"
        data = urllib.request.urlopen(url).read().decode('utf-8')
        header = urllib.request.urlopen(url).readline().decode('utf-8').replace('\n', '')
        header = header[3:]
        # remove newline characters
        data = data.replace("\n", "")
        # split around digit to find end of header
        datalist = re.split("\d", data)
        # take everything after the version number and assign it to sequence
        sequence = datalist[-1]
        # remove line referance
    # take the first line of the faster file as the header



    # retrun key value pair dictionary
    fasta = {'Header': header, 'Sequence': sequence}
    return fasta

#given a sequence and a pattern
def motifsearch(sequence, repattern):
    if not repattern:
      repattern = r'(?=([^p])([^pkrhw])([vlswfnq])([iltywfn])([fiy])([^pkrh]))'
    regex = re.compile(repattern.upper())
    matchlist = []
    for match in regex.finditer(sequence):
        matchlist.append(match)
        #print("%s: %s" % (match.start(), match.group()))
        #returns a list containing matched characters and their positions
    return matchlist




# url for hompage
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        form = request.form
        acession = form.get("acession")
        header = form.get("header")
        fastaseq = form.get("fasta")
        print(acession)
        print(fastaseq)
        print(header)
        if acession:
            if validateinput(acession) != False:
                print("sucess")
                fasta = getfasta(acession, None, None)
                print(fasta['Sequence'])
                outputheader = fasta['Header']
                outputsequence = (fasta['Sequence'])
                matches = motifsearch(fasta['Sequence'], None)
                outputmatch = []
                outputpos = []
                string = []
                for items in matches:
                    outputpos.append(items.start())
                    outputmatch.append("".join(items.group(1,2,3,4,5,6)))
                    #for char in tuple:
                    #    string.append(char)
                print(outputheader)
                print(outputsequence)
                print(outputpos)
                print(outputmatch)
                return render_template("index.html", error= "valid code submitted", resulthead=outputheader, resultseq=outputsequence, pattern=pattern, resultmatches=outputmatch, resultpos=outputpos)
            else:
                return render_template("index.html", error="Error:not valid acession code")

        if fastaseq and header:
            print("fastasucess")
            fasta = getfasta(None, fastaseq, header)
            print(fasta['Sequence'])
            outputheader = fasta['Header']
            outputsequence = (fasta['Sequence'])
            matches = motifsearch(fasta['Sequence'], None)
            outputmatch = []
            outputpos = []
            for items in matches:
                outputpos.append(items.start())
                outputmatch.append(items.group())
            print(outputheader)
            print(outputsequence)
            print(outputpos)
            print(outputmatch)
            return render_template("index.html", error="valid code submitted", resulthead=outputheader,
                                   resultseq=outputsequence, pattern=pattern, resultmatches=outputmatch,
                                   resultpos=outputpos)

        if acession != None and fastaseq != None and header != None:
            error_string = "Error: No acession or fasta and header provided"
            return render_template("index.html", error=error_string)


    # define template amd pass ,template name = python name
    return render_template('index.html', variable=var)

# url for download
@app.route('/guide')
def guide():
        return render_template("guide.html")

 # url for download
@app.route('/download')
def download():
    # with open("outputs/Adjacency.csv") as fp:
    #     csv = fp.read()
    f = open('download.txt', 'r+')
    f.write('0123456789abcdef')
    f.close()
    return send_file("download.txt",mimetype="text/csv")

# loads templates
template_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader("templates")
])
# actually loads the templates
app.jinja_loader = template_loader


# run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0" ,port=80)

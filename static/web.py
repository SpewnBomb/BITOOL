from flask import Flask, request, render_template, send_file
import jinja2
import re
import urllib

app = Flask(__name__)

#test variable
var = "variable"
#accession gloabl
acession = ""
#default patter
pattern = r'([^p])([^pkrhw])([vlswfnq])([iltywfn])([fiy])([^pkrh])'
#global error
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

def validfasta(fasta):
    amino_acid = re.compile("r'[CDSQKPTFAXGIELHRWMNYV\s?\"?]*")
    fasta = fasta.upper()
    if(re.fullmatch(amino_acid,fasta) == True):
        print("fullmatchtruefasta")
        return True

    else:
        print("falsefasta")
        return False

#can either take an accession code or the raw data and header
def getfasta(accessioncode , data, header):
    #if raw input given make sure there arn't newline and spaces if the copied and pasted it
    if accessioncode == None:
        data = data.replace("\n", "")
        data = data.replace(" ", "")
        sequence = data
    #if no raw input the build and fetch from url
    if data == None and header == None:
        url = "http://www.uniprot.org/uniprot/" + accessioncode + ".fasta"
        #turn bytes into a workable string
        data = urllib.request.urlopen(url).read().decode('utf-8')
        header = urllib.request.urlopen(url).readline().decode('utf-8').replace('\n', '')
        header = header[3:]
        # remove newline characters
        data = data.replace("\n", "")
        # split around digit to find end of header
        datalist = re.split("\d", data)
        # take everything after the version number and assign it to sequence (could fail without version number but works for now)
        sequence = datalist[-1]
        # remove line referance
    # take the first line of the faster file as the header



    # retrun key value pair dictionary
    fasta = {'Header': header, 'Sequence': sequence}
    return fasta

#given a sequence and a pattern possibly expandable to be passed own motif
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


#flask stuff

# url for hompage
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        form = request.form
        acession = form.get("acession")
        header = form.get("header")
        fastaseq = form.get("fasta")
        # print(acession)
        # print(fastaseq)
        # print(header)
        if acession:
            if validateinput(acession) != False:
                #print("sucess")
                fasta = getfasta(acession, None, None)
                #print(fasta['Sequence'])
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
                # print(outputheader)
                # print(outputsequence)
                # print(outputpos)
                # print(outputmatch)
                color = "color:green;"
                return render_template("index.html", error="valid code submitted" , errorcolor=color, resulthead=outputheader, resultseq=outputsequence, pattern=pattern, resultmatches=outputmatch, resultpos=outputpos)
            else:
                color = "color:red;"
                return render_template("index.html", error="Error: invalid acession code format",  errorcolor=color)

        if fastaseq and header:
            print("fastasucess")
            fasta = getfasta(None, fastaseq, header)
            #print(fasta['Sequence'])
            outputheader = fasta['Header']
            outputsequence = (fasta['Sequence'])
            if(validfasta(outputsequence)):
                matches = motifsearch(fasta['Sequence'], None)
                outputmatch = []
                outputpos = []
                for items in matches:
                    outputpos.append(items.start())
                    outputmatch.append("".join(items.group(1, 2, 3, 4, 5, 6)))
                #print(outputheader)
                # print(outputsequence)
                # print(outputpos)
                # print(outputmatch)
                color = "color:green;"
                return render_template("index.html", error="valid code submitted",errorcolor=color, resulthead=outputheader,
                                       resultseq=outputsequence, pattern=pattern, resultmatches=outputmatch,
                                       resultpos=outputpos)
            else:
                color = "color:red;"
                return render_template("index.html", error="fasta sequence contained invlaid symbols", errorcolor=color,)


        if acession != None and fastaseq != None and header != None:
            error_string = "Error: No acession or fasta and header were incomplete"
            color = "color:red;"
            return render_template("index.html", error=error_string,errorcolor=color)


    # define template amd pass ,template name = python name
    return render_template('index.html')

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

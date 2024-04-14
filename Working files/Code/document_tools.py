#this module contains document transformers

#ask user for input XML file containing words; outputs another XML file with the words broken into syllables
#pass in an lxml etree object and a wordhandler object
def syllabify(ET, wh):
    import re
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    #Get the input file and attempt to parse it
    file_path = filedialog.askopenfilename()
    doc=None
    if len(file_path)>0:
        fin = open(file_path, "r")
        doc=ET.parse(file_path)
        fin.close
        
    if doc == None: return None
    
    root=doc.getroot()
    if root == None: return None

    try:
        lang=str(root.xpath("./teiHeader/profileDesc/langUsage/language/@ident")[0])
    except: lang="TEIerror"
    lang=lang.strip()
    if lang=="oe":
        wh.language=0
    elif lang=="osx":
        wh.language=1
    elif lang=="on":
        wh.language=2
    try:
        syll_mthd=str(root.xpath("./teiHeader/profileDesc/langUsage/language/@syllabification")[0])
    except: 
        syll_mthd="TEIerror"
    syll_mthd=syll_mthd.strip()
    if syll_mthd=="coda" or syll_mthd=="codamax": wh.codamax=True
    print(syll_mthd)

    #get all the word elements
    words = doc.findall("w")
    syllables=[]
    syllables.clear
    
    

    #we will assign an ID to each word as part of the syllabification process
    wordvars={"id":0}

    #this is where we will do the work of restructuring the xml and attaching the syllables
    def buildWord(word, wordvars,parent=None):
        #first assign the word an ID
        word.set("id",str(wordvars['id'])); wordvars['id'] +=1
        #now get the text of the word to break into syllables; the next several lines need cleaning up
        try:
            text_exists=(len(word.text)!=0)
        except:
            text_exists=False
        if text_exists: 
            text = word.text
            syllables = wh.break_word(text)
            if syllables != None:
                syllCount=len(syllables)
                word.set("Σ",str(syllCount)) #store the syllable count on the <w> element to make later calculations
                i=syllCount-1
                for syl in syllables:
                    allit=None
                    #create a new, unattached syllable node
                    # sylEl=doc.createElement("s")
                    sylEl=ET.Element("s")

                    #add the syllable text
                    sylEl.text=syllables[i][0]
                    #put the mora count in an attribute
                    sylEl.set("m", str(syllables[i][1]))
                    sylEl.set("wt", str(syllables[i][2]))
                    try:
                        allit=syllables[i][3]
                    except:
                        allit=None

                    #if the present word could carry stress, add the alliterative symbol to the root syllable
                    if allit!=None: #and word.get("wc")!="c"
                        sylEl.set("A",allit)
                    
    
                    #now attach the syllable element to the parent word element 
                    if parent==None:
                        word.addnext(sylEl)
                    else:
                        parent.addnext(sylEl)
                        word.tail=None
                    i -=1 
                #the word text is now in the <s> elements; get rid of the text node in <w>
                word.text = None
            return 0

    for word in words: 
        if len(word)>0: #if there are child words
            for subword in reversed(word): 
                buildWord(subword, wordvars, word)
                word.addnext(subword) #promote it to a sibling
        buildWord(word, wordvars)
        

    #write the output
    file_path = filedialog.askopenfilename()
                        
    if len(file_path)>0:
        f = open(file_path, 'w')
        xml = ET.tostring(doc, encoding="unicode")
        f.write(xml)
        f.close()
        
    return 0

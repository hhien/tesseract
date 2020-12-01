#! /usr/bin/python
# -*- coding: utf-8 -*-

# author: Ha Thi Hien
# description: Run tesseract OCR, output json file for CUTIE
# date: 1.12.2020

from PIL import Image
import pytesseract
import sys
# from lxml import etree
from os.path import split, splitext
import json

def readTSV(data):
    rows = data.split('\n')
    nlen = len(rows)
    if nlen == 0:
        return
    doc = []
    # get columns
    c = dict() # column
    #level	page_num	block_num	par_num	line_num	word_num	left	top	width	height	conf	text
    header = rows[0].split('\t')    

    npage = None # page#
    nbl = None
    nline = None
    for i in range(1, nlen):
        r = rows[i].split('\t')        
        word = dict()
        word['id'] = i        
        word['bbox'] = tuple([int(r[6]), int(r[7]), int(r[6])+ int(r[8]), int(r[7])+ int(r[9])])
        if len(r) < 12:
            #sys.stderr.write('not full fields')            
            word['text'] = ""
        else:
            word['text'] = r[11]
        if word['text']:            
            doc.append(word)
    return doc


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Doing TesseractOCR')
    
    parser.add_argument('-i', '--input', type=str,
                        required=False, default=sys.stdin,
                        help='Input image file')
    parser.add_argument('-l', '--language', type=str,
                        required=False, default='eng',
                        help='language')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        required=False, default=sys.stdout,
                        help='Output')
    
    args = parser.parse_args()
    
    with Image.open(args.input) as img:
        # width, height = img.size
        doc = pytesseract.image_to_data(img, lang=args.language, config='--psm 11')#custom_config
        
        doc = readTSV(doc)
        
        new_doc = {}
        new_doc.update({'text_boxes':doc})

        classes = ['O', 'DATE_SALE', 'ADDRESS_SELLER', 'DOC_NR', 'DATE_CREATION', 'ADDRESS_CONTRACTOR', 'VAT_ID_CONTRACTOR', 'PAYMENT_METHOD', 'VAT_ID_SELLER', 'PAYMENT_BANK_NR', 'TOTAL_PAY', 'TOTAL_CURRENCY', 'TOTAL_TAX', 'TOTAL_WITH_TAX', 'TOTAL_WITHOUT_TAX', 'DATE_PAYMENT', 'NAME_SELLER', 'NAME_CONTRACTOR']
        fields = []
        for cl in classes:
            new_field = {"field_name": cl, "value_id": [], "value_text":[], "key_id":[], "key_text":[]}
            fields.append(new_field)
        new_doc.update({'fileds': fields})

        new_doc.update({"global_attributes":{"file_id": args.input}})        
        
        json_obj = json.dumps(new_doc, indent = 4, ensure_ascii=False)
        
        args.output.write(json_obj)


if __name__ == "__main__":
    main()

import zipfile
import xml.etree.ElementTree as ET
import os

docx_path = r"c:\Users\Kaustubh\OneDrive\Desktop\HACKMATRIX\formula_sheet.docx"
output_md = r"C:\Users\Kaustubh\.gemini\antigravity-ide\brain\005755e6-3389-46f6-89de-45af2aac6789\scratch\formula_sheet.md"

os.makedirs(os.path.dirname(output_md), exist_ok=True)

with zipfile.ZipFile(docx_path) as z:
    xml_content = z.read("word/document.xml")

tree = ET.fromstring(xml_content)
namespaces = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'
}

paragraphs = []
for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
    texts = []
    for node in p.iter():
        if node.tag.endswith('}t'):
            if node.text:
                texts.append(node.text)
    if texts:
        paragraphs.append(''.join(texts))

with open(output_md, 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(paragraphs))

print(f"Extracted {len(paragraphs)} paragraphs to {output_md}")

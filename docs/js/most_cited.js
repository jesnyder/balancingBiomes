/*
===========================================================
MOST CITED RESEARCH TABLE — TABULATOR SETUP
===========================================================

REQUIRED HTML (paste this in index.html):

1️⃣ Include Tabulator CSS + JS (once):
-----------------------------------------------------------
<link href="https://unpkg.com/tabulator-tables@5.5.0/dist/css/tabulator.min.css" rel="stylesheet">
<script src="https://unpkg.com/tabulator-tables@5.5.0/dist/js/tabulator.min.js"></script>

2️⃣ Add button + table container:
-----------------------------------------------------------
<button id="download-most-cited">Download Table</button>
<div id="most-cited-research-table"></div>

3️⃣ Include this JS file AFTER the div:
-----------------------------------------------------------
<script src="docs/js/most_cited.js"></script>

WHY:
- Tabulator requires the div to exist before initialization
- Data is embedded directly (no AJAX)
- Avoids 404 and CORS issues
===========================================================
*/

document.addEventListener("DOMContentLoaded", function() {

    const tableData = [
    {
        "title": "Comparative Genomics in Salt Tolerance between Arabidopsis and Arabidopsis-Related Halophyte Salt Cress Using Arabidopsis Microarray",
        "authors": "Teruaki Taji, Motoaki Seki, Masakazu Satou, Tetsuya Sakurai, Masatomo Kobayashi, Kanako Ishiyama, Yoshihiro Narusaka, Mari Narusaka, Jian-Kang Zhu, Kazuo Shinozaki",
        "year": 2004,
        "journal": "",
        "citations": 497,
        "url": "https://doi.org/10.1104/pp.104.039909"
    },
    {
        "title": "Salt Cress. A Halophyte and Cryophyte Arabidopsis Relative Model System and Its Applicability to Molecular Genetic Analyses of Growth and Development of Extremophiles",
        "authors": "Gu\u0308nsu Inan, Quan Zhang, Pinghua Li, Zenglan Wang, Ziyi Cao, Hui Zhang, Changqing Zhang, Tanya M. Quist, S. Mark Goodwin, Jianhua Zhu, Huazhong Shi, Barbara Damsz, Tarif Charbaji, Qingqiu Gong, Shisong Ma, Mark Fredricksen, David W. Galbraith, Matthew A. Jenks, David Rhodes, Paul M. Hasegawa, Hans J. Bohnert, Robert J. Joly, Ray A. Bressan, Jian-Kang Zhu",
        "year": 2004,
        "journal": "",
        "citations": 454,
        "url": "https://doi.org/10.1104/pp.104.041723"
    },
    {
        "title": "Mining Halophytes for Plant Growth-Promoting Halotolerant Bacteria to Enhance the Salinity Tolerance of Non-halophytic Crops",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 435,
        "url": ""
    },
    {
        "title": "Halophyte agriculture: Success stories",
        "authors": "Suresh Panta, Tim Flowers, Peter Lane, Richard Doyle, Gabriel Haros, Sergey Shabala",
        "year": 2014,
        "journal": "",
        "citations": 427,
        "url": "https://doi.org/10.1016/j.envexpbot.2014.05.006"
    },
    {
        "title": "Isolation, Characterization, and Use for Plant Growth Promotion Under Salt Stress, of ACC Deaminase-Producing Halotolerant Bacteria Derived from Coastal Soil",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 401,
        "url": ""
    },
    {
        "title": "Salinity effects on polyphenol content and antioxidant activities in leaves of the halophyte Cakile maritima",
        "authors": "Riadh Ksouri, Wided Megdiche, Ahmed Debez, Hanen Falleh, Claude Grignon, Chedly Abdelly",
        "year": 2007,
        "journal": "",
        "citations": 399,
        "url": "https://doi.org/10.1016/j.plaphy.2007.02.001"
    },
    {
        "title": "Contrasting Responses of Photosynthesis to Salt Stress in the Glycophyte Arabidopsis and the Halophyte Thellungiella: Role of the Plastid Terminal Oxidase as an Alternative Electron Sink",
        "authors": "Piotr Stepien, Giles N. Johnson",
        "year": 2008,
        "journal": "",
        "citations": 369,
        "url": "https://doi.org/10.1104/pp.108.132407"
    },
    {
        "title": "Isolation and characterization of endophytic plant growth-promoting (PGPB) or stress homeostasis-regulating (PSHB) bacteria associated to the halophyte Prosopis strombulifera",
        "authors": "Ver\u00f3nica Sgroy, Fabricio Cass\u00e1n, Oscar Masciarelli, Mar\u00eda Florencia Del Papa, Antonio Lagares, Virginia Luna",
        "year": 2009,
        "journal": "",
        "citations": 333,
        "url": "https://doi.org/10.1007/s00253-009-2116-3"
    },
    {
        "title": "Proteomics, metabolomics, and ionomics perspectives of salinity tolerance in halophytes",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 301,
        "url": ""
    },
    {
        "title": "Osmotic adjustment and ion balance traits of an alkali resistant halophyte Kochia sieversiana during adaptation to salt and alkali conditions",
        "authors": "Chunwu Yang, Jianna Chong, Changyou Li, Changmin Kim, Decheng Shi, Deli Wang",
        "year": 2007,
        "journal": "",
        "citations": 301,
        "url": "https://doi.org/10.1007/s11104-007-9251-3"
    },
    {
        "title": "Enhanced growth of halophyte plants in biochar\u2010amended coastal soil: roles of nutrient availability and rhizosphere microbial modulation",
        "authors": "Hao Zheng, Xiao Wang, Lei Chen, Zhenyu Wang, Yang Xia, Yipeng Zhang, Hefang Wang, Xianxiang Luo, Baoshan Xing",
        "year": 2017,
        "journal": "",
        "citations": 283,
        "url": "https://doi.org/10.1111/pce.12944"
    },
    {
        "title": "Halotolerant Rhizobacteria Promote Growth and Enhance Salinity Tolerance in Peanut",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 282,
        "url": ""
    },
    {
        "title": "Compatible Solute Engineering in Plants for Abiotic Stress Tolerance - Role of Glycine Betaine",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 280,
        "url": ""
    },
    {
        "title": "Halophyte crop cultivation: The case for Salicornia and Sarcocornia",
        "authors": "Yvonne Ventura, Moshe Sagi",
        "year": 2013,
        "journal": "",
        "citations": 274,
        "url": "https://doi.org/10.1016/j.envexpbot.2012.07.010"
    },
    {
        "title": "Physiological and antioxidant responses of the perennial halophyte Crithmum maritimum to salinity",
        "authors": "Nader Ben Amor, Karim Ben Hamed, Ahmed Debez, Claude Grignon, Chedly Abdelly",
        "year": 2005,
        "journal": "",
        "citations": 274,
        "url": "https://doi.org/10.1016/j.plantsci.2004.11.002"
    },
    {
        "title": "Halo-tolerant plant growth promoting rhizobacteria for improving productivity and remediation of saline soils",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 273,
        "url": ""
    },
    {
        "title": "Halophyte seed germination",
        "authors": "Irwin A. Ungar",
        "year": 1978,
        "journal": "",
        "citations": 258,
        "url": "https://doi.org/10.1007/bf02919080"
    },
    {
        "title": "The development of halophyte-based agriculture: past and present",
        "authors": "Yvonne Ventura, Amram Eshel, Dov Pasternak, Moshe Sagi",
        "year": 2014,
        "journal": "",
        "citations": 252,
        "url": "https://doi.org/10.1093/aob/mcu173"
    },
    {
        "title": "Effects of salt treatment and osmotic stress on V\u2010ATPase and V\u2010PPase in leaves of the halophyte Suaeda salsa",
        "authors": "Baoshan Wang, Ulrich L\u00fcttge, Rafael Ratajczak",
        "year": 2001,
        "journal": "",
        "citations": 251,
        "url": "https://doi.org/10.1093/jexbot/52.365.2355"
    },
    {
        "title": "Germination strategies of halophyte seeds under salinity",
        "authors": "Bilquees Gul, Raziuddin Ansari, Timothy J. Flowers, M. Ajmal Khan",
        "year": 2013,
        "journal": "",
        "citations": 245,
        "url": "https://doi.org/10.1016/j.envexpbot.2012.11.006"
    },
    {
        "title": "Effects of Abiotic Stress on Soil Microbiome",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 241,
        "url": ""
    },
    {
        "title": "Antioxidant and antimicrobial activities of the edible medicinal halophyte Tamarix gallica L. and related polyphenolic constituents",
        "authors": "Riadh Ksouri, Hanen Falleh, Wided Megdiche, Najla Trabelsi, Baya Mhamdi, Kamel Chaieb, Amina Bakrouf, Christian Magn\u00e9, Chedly Abdelly",
        "year": 2009,
        "journal": "",
        "citations": 241,
        "url": "https://doi.org/10.1016/j.fct.2009.05.040"
    },
    {
        "title": "The roots of the halophyte Salicornia brachiata are a source of new halotolerant diazotrophic bacteria with plant growth-promoting potential",
        "authors": "Bhavanath Jha, Iti Gontia, Anton Hartmann",
        "year": 2011,
        "journal": "",
        "citations": 240,
        "url": "https://doi.org/10.1007/s11104-011-0877-9"
    },
    {
        "title": "Salinity effects on germination, growth, and seed production of the halophyte Cakile maritima",
        "authors": "Ahmed Debez, Karim Ben Hamed, Claude Grignon, Chedly Abdelly",
        "year": 2004,
        "journal": "",
        "citations": 221,
        "url": "https://doi.org/10.1023/b:plso.0000037034.47247.67"
    },
    {
        "title": "How can we take advantage of halophyte properties to cope with heavy metal toxicity in salt-affected areas?",
        "authors": "Stanley Lutts, Isabelle Lef\u00e8vre",
        "year": 2015,
        "journal": "",
        "citations": 218,
        "url": "https://doi.org/10.1093/aob/mcu264"
    },
    {
        "title": "<i>Salicornia bigelovii</i>\n            Torr.: An Oilseed Halophyte for Seawater Irrigation",
        "authors": "Edward P. Glenn, James W. O'Leary, M. Carolyn Watson, T. Lewis Thompson, Robert O. Kuehl",
        "year": 1991,
        "journal": "",
        "citations": 217,
        "url": "https://doi.org/10.1126/science.251.4997.1065"
    },
    {
        "title": "Fungi as a Potential Source of Pigments: Harnessing Filamentous Fungi",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 214,
        "url": ""
    },
    {
        "title": "Effects of Salinity on Growth, Water Relations and Ion Accumulation of the Subtropical Perennial Halophyte, Atriplex griffithii var. stocksii",
        "authors": "M KHAN",
        "year": 2000,
        "journal": "",
        "citations": 213,
        "url": "https://doi.org/10.1006/anbo.1999.1022"
    },
    {
        "title": "Evidence that differential gene expression between the halophyte, <i>Thellungiella halophila</i>, and <i>Arabidopsis thaliana</i> is responsible for higher levels of the compatible osmolyte proline and tight control of Na<sup>+</sup> uptake in <i>T.\u2003halophila</i>",
        "authors": "SURYA KANT, PRAGYA KANT, ERAN RAVEH, SIMON BARAK",
        "year": 2006,
        "journal": "",
        "citations": 206,
        "url": "https://doi.org/10.1111/j.1365-3040.2006.01502.x"
    },
    {
        "title": "The effect of salinity on the growth, water status, and ion content of a leaf succulent perennial halophyte, Suaeda fruticosa (L.) Forssk",
        "authors": "M Ajmal Khan, Irwin A Ungar, Allan M Showalter",
        "year": 2000,
        "journal": "",
        "citations": 205,
        "url": "https://doi.org/10.1006/jare.1999.0617"
    },
    {
        "title": "Specialized Microbiome of a Halophyte and its Role in Helping Non-Host Plants to Withstand Salinity",
        "authors": "Zhilin Yuan, Irina S. Druzhinina, Jessy Labb\u00e9, Regina Redman, Yuan Qin, Russell Rodriguez, Chulong Zhang, Gerald A. Tuskan, Fucheng Lin",
        "year": 2016,
        "journal": "",
        "citations": 192,
        "url": "https://doi.org/10.1038/srep32467"
    },
    {
        "title": "Isolation of ACC deaminase-producing habitat-adapted symbiotic bacteria associated with halophyte Limonium sinense (Girard) Kuntze and evaluating their plant growth-promoting activity under salt stress",
        "authors": "Sheng Qin, Yue-Ji Zhang, Bo Yuan, Pei-Yuan Xu, Ke Xing, Jun Wang, Ji-Hong Jiang",
        "year": 2013,
        "journal": "",
        "citations": 190,
        "url": "https://doi.org/10.1007/s11104-013-1918-3"
    },
    {
        "title": "Biological indicators for pollution detection in terrestrial and aquatic ecosystems",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 185,
        "url": ""
    },
    {
        "title": "Properties of the halophyte microbiome and their implications for plant salt tolerance",
        "authors": "Silke Ruppel, Philipp Franken, Katja Witzel",
        "year": 2013,
        "journal": "",
        "citations": 184,
        "url": "https://doi.org/10.1071/fp12355"
    },
    {
        "title": "Rapid regulation of the plasma membrane H+-ATPase activity is essential to salinity tolerance in two halophyte species, Atriplex lentiformis and Chenopodium quinoa",
        "authors": "Jayakumar Bose, Ana Rodrigo-Moreno, Diwen Lai, Yanjie Xie, Wenbiao Shen, Sergey Shabala",
        "year": 2014,
        "journal": "",
        "citations": 184,
        "url": "https://doi.org/10.1093/aob/mcu219"
    },
    {
        "title": "Salt stimulation of growth and photosynthesis in an extreme halophyte, Arthrocnemum macrostachyum",
        "authors": "S. Redondo-G\u00c3\u00b3mez, E. Mateos-Naranjo, M. E. Figueroa, A. J. Davy",
        "year": 2010,
        "journal": "",
        "citations": 183,
        "url": "https://doi.org/10.1111/j.1438-8677.2009.00207.x"
    },
    {
        "title": "Salinity treatment shows no effects on photosystem II photochemistry, but increases the resistance of photosystem II to heat stress in halophyte Suaeda salsa",
        "authors": "C. Lu",
        "year": 2003,
        "journal": "",
        "citations": 183,
        "url": "https://doi.org/10.1093/jxb/erg080"
    },
    {
        "title": "Metabolome and water homeostasis analysis of Thellungiella salsuginea suggests that dehydration tolerance is a key response to osmotic stress in this halophyte",
        "authors": "Rapha\u00ebl Lugan, Marie-Fran\u00e7oise Niogret, Laurent Leport, Jean-Paul Gu\u00e9gan, Fran\u00e7ois Robert Larher, Arnould Savour\u00e9, Joachim Kopka, Alain Bouchereau",
        "year": 2010,
        "journal": "",
        "citations": 177,
        "url": "https://doi.org/10.1111/j.1365-313x.2010.04323.x"
    },
    {
        "title": "Photosynthesis, photosystem II efficiency and the xanthophyll cycle in the salt\u2010adapted halophyte <i>Atriplex centralasiatica</i>",
        "authors": "Nianwei Qiu, Qingtao Lu, Congming Lu",
        "year": 2003,
        "journal": "",
        "citations": 176,
        "url": "https://doi.org/10.1046/j.1469-8137.2003.00825.x"
    },
    {
        "title": "Early effects of salt stress on the physiological and oxidative status of <i>Cakile maritima</i> (halophyte) and <i>Arabidopsis thaliana</i> (glycophyte)",
        "authors": "Hasna Ellouzi, Karim Ben Hamed, Jana Cela, Sergi Munn\u00e9\u2010Bosch, Chedly Abdelly",
        "year": 2011,
        "journal": "",
        "citations": 174,
        "url": "https://doi.org/10.1111/j.1399-3054.2011.01450.x"
    },
    {
        "title": "Potential for Plant Growth Promotion of Rhizobacteria Associated with<i>Salicornia</i>Growing in Tunisian Hypersaline Soils",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 173,
        "url": ""
    },
    {
        "title": "Halomonas organivorans sp. nov., a moderate halophile able to degrade aromatic compounds",
        "authors": "Mar\u00eda Teresa Garc\u00eda, Encarnaci\u00f3n Mellado, Juan Carlos Ostos, Antonio Ventosa",
        "year": 2004,
        "journal": "",
        "citations": 171,
        "url": "https://doi.org/10.1099/ijs.0.63114-0"
    },
    {
        "title": "Effect of saline water on seed germination and early seedling growth of the halophyte quinoa",
        "authors": "M. R. Panuccio, S. E. Jacobsen, S. S. Akhtar, A. Muscolo",
        "year": 2014,
        "journal": "",
        "citations": 169,
        "url": "https://doi.org/10.1093/aobpla/plu047"
    },
    {
        "title": "Halobacterium mediterranei spec, nov., a New Carbohydrate-Utilizing Extreme Halophile",
        "authors": "F. Rodriguez-Valera, Guadalupe Juez, D.J. Kushner",
        "year": 1983,
        "journal": "",
        "citations": 167,
        "url": "https://doi.org/10.1016/s0723-2020(83)80021-6"
    },
    {
        "title": "Microbulbifer\n            salipaludis sp. nov., a moderate halophile isolated from a Korean salt marsh",
        "authors": "Jung-Hoon Yoon, In-Gi Kim, Dong-Yeon Shin, Kook Hee Kang, Yong-Ha Park",
        "year": 2003,
        "journal": "",
        "citations": 165,
        "url": "https://doi.org/10.1099/ijs.0.02342-0"
    },
    {
        "title": "Root exudates-driven rhizosphere recruitment of the plant growth-promoting rhizobacterium Bacillus flexus KLBMP 4941 and its growth-promoting effect on the coastal halophyte Limonium sinense under salt stress",
        "authors": "You-Wei Xiong, Xue-Wei Li, Tian-Tian Wang, Yuan Gong, Chun-Mei Zhang, Ke Xing, Sheng Qin",
        "year": 2020,
        "journal": "",
        "citations": 163,
        "url": "https://doi.org/10.1016/j.ecoenv.2020.110374"
    },
    {
        "title": "Living at the Frontiers of Life: Extremophiles in Chile and Their Potential for Bioremediation",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 162,
        "url": ""
    },
    {
        "title": "A novel methyl transferase induced by osmotic stress in the facultative halophyte Mesembryanthemum crystallinum.",
        "authors": "D.M. Vernon, H.J. Bohnert",
        "year": 1992,
        "journal": "",
        "citations": 162,
        "url": "https://doi.org/10.1002/j.1460-2075.1992.tb05266.x"
    },
    {
        "title": "NaCl Regulation of Plasma Membrane H+-ATPase Gene Expression in a Glycophyte and a Halophyte",
        "authors": "X. Niu, M. L. Narasimhan, R. A. Salzman, R. A. Bressan, P. M. Hasegawa",
        "year": 1993,
        "journal": "",
        "citations": 161,
        "url": "https://doi.org/10.1104/pp.103.3.713"
    },
    {
        "title": "Salt-Tolerant Halophyte Rhizosphere Bacteria Stimulate Growth of Alfalfa in Salty Soil",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 160,
        "url": ""
    },
    {
        "title": "Halophyte Improvement for a Salinized World",
        "authors": "Cheng-Jiang Ruan, Jaime A. Teixeira da Silva, Susan Mopper, Pei Qin, Stanley Lutts",
        "year": 2010,
        "journal": "",
        "citations": 156,
        "url": "https://doi.org/10.1080/07352689.2010.524517"
    },
    {
        "title": "Management of Phosphorus in Salinity-Stressed Agriculture for Sustainable Crop Production by Salt-Tolerant Phosphate-Solubilizing Bacteria\u2014A Review",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 155,
        "url": ""
    },
    {
        "title": "Low-Affinity Na+ Uptake in the Halophyte<i>Suaeda maritima</i>\u00a0",
        "authors": "Suo-Min Wang, Jin-Lin Zhang, Timothy J. Flowers",
        "year": 2007,
        "journal": "",
        "citations": 154,
        "url": "https://doi.org/10.1104/pp.107.104315"
    },
    {
        "title": "Isolation and characterization of a Na+/H+ antiporter gene from the halophyte Atriplex gmelini",
        "authors": "Akira Hamada, Mariko Shono, Tao Xia, Masaru Ohta, Yasuyuki Hayashi, Akira Tanaka, Takahiko Hayakawa",
        "year": 2001,
        "journal": "",
        "citations": 154,
        "url": "https://doi.org/10.1023/a:1010603222673"
    },
    {
        "title": "An inland and a coastal population of the Mediterranean xero-halophyte species Atriplex halimus L. differ in their ability to accumulate proline and glycinebetaine in response to salinity and water stress",
        "authors": "A. B. Hassine, M. E. Ghanem, S. Bouzid, S. Lutts",
        "year": 2008,
        "journal": "",
        "citations": 152,
        "url": "https://doi.org/10.1093/jxb/ern040"
    },
    {
        "title": "Reduced Tonoplast Fast-Activating and Slow-Activating Channel Activity Is Essential for Conferring Salinity Tolerance in a Facultative Halophyte, Quinoa\n\u00a0\n\u00a0\n\u00a0",
        "authors": "Edgar Bonales-Alatorre, Sergey Shabala, Zhong-Hua Chen, Igor Pottosin",
        "year": 2013,
        "journal": "",
        "citations": 149,
        "url": "https://doi.org/10.1104/pp.113.216572"
    },
    {
        "title": "Heavy Metal Accumulation by the Halophyte Species Mediterranean Saltbush",
        "authors": "Stanley Lutts, Isabelle Lef\u00e8vre, Christine Delp\u00e9r\u00e9e, Sandrine Kivits, Caroline Dechamps, Antonio Robledo, Enrique Correal",
        "year": 2004,
        "journal": "",
        "citations": 148,
        "url": "https://doi.org/10.2134/jeq2004.1271"
    },
    {
        "title": "Response of antioxidant systems to NaCl stress in the halophyte <i>Cakile maritima</i>",
        "authors": "Nader Ben Amor, Ana Jim\u00e9nez, Wided Megdiche, Marianne Lundqvist, Francisca Sevilla, Chedly Abdelly",
        "year": 2006,
        "journal": "",
        "citations": 144,
        "url": "https://doi.org/10.1111/j.1399-3054.2006.00620.x"
    },
    {
        "title": "NaCl alleviates polyethylene glycol-induced water stress in the halophyte species Atriplex halimus L.",
        "authors": "Juan-Pablo Mart\u00ednez, Jean-Marie Kinet, Mohammed Bajji, Stanley Lutts",
        "year": 2005,
        "journal": "",
        "citations": 143,
        "url": "https://doi.org/10.1093/jxb/eri235"
    },
    {
        "title": "Plant growth-promoting rhizobacteria: Salt stress alleviators to improve crop productivity for sustainable agriculture development",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 142,
        "url": ""
    },
    {
        "title": "Growth and photosynthetic responses to salinity in an extreme halophyte, <i>Sarcocornia fruticosa</i>",
        "authors": "Susana Redondo\u2010G\u00f3mez, Clare Wharmby, Jes\u00fas M. Castillo, Enrique Mateos\u2010Naranjo, Carlos J. Luque, Alfonso De Cires, Teresa Luque, Anthony J. Davy, M. Enrique Figueroa",
        "year": 2006,
        "journal": "",
        "citations": 140,
        "url": "https://doi.org/10.1111/j.1399-3054.2006.00719.x"
    },
    {
        "title": "Salt Stress Induced Differential Proteome and Metabolome Response in the Shoots of <i>Aeluropus lagopoides</i> (Poaceae), a Halophyte C<sub>4</sub> Plant",
        "authors": "Hamid Sobhanian, Nasrin Motamed, Ferdous Rastgar Jazii, Takuji Nakamura, Setsuko Komatsu",
        "year": 2010,
        "journal": "",
        "citations": 139,
        "url": "https://doi.org/10.1021/pr900974k"
    },
    {
        "title": "Epidermal bladder cells confer salinity stress tolerance in the halophyte quinoa and Atriplex species",
        "authors": "Ali Kiani\u2010Pouya, Ute Roessner, Nirupama S. Jayasinghe, Adrian Lutz, Thusitha Rupasinghe, Nadia Bazihizina, Jennifer Bohm, Sulaiman Alharbi, Rainer Hedrich, Sergey Shabala",
        "year": 2017,
        "journal": "",
        "citations": 138,
        "url": "https://doi.org/10.1111/pce.12995"
    },
    {
        "title": "Mechanisms and Strategies of Plant Microbiome Interactions to Mitigate Abiotic Stresses",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 137,
        "url": ""
    },
    {
        "title": "Comparative Proteomics of Thellungiella halophila Leaves from Plants Subjected to Salinity Reveals the Importance of Chloroplastic Starch and Soluble Sugars in Halophyte Salt Tolerance",
        "authors": "Xuchu Wang, Lili Chang, Baichen Wang, Dan Wang, Pinghua Li, Limin Wang, Xiaoping Yi, Qixing Huang, Ming Peng, Anping Guo",
        "year": 2013,
        "journal": "",
        "citations": 137,
        "url": "https://doi.org/10.1074/mcp.m112.022475"
    },
    {
        "title": "Coordinated Changes in Antioxidative Enzymes Protect the Photosynthetic Machinery from Salinity Induced Oxidative Damage and Confer Salt Tolerance in an Extreme Halophyte Salvadora persica L.",
        "authors": "Jaykumar Rangani, Asish K. Parida, Ashok Panda, Asha Kumari",
        "year": 2016,
        "journal": "",
        "citations": 136,
        "url": "https://doi.org/10.3389/fpls.2016.00050"
    },
    {
        "title": "Production of amylase by newly isolated moderate halophile, Halobacillus sp. strain MA-2",
        "authors": "M.A Amoozegar, F Malekzadeh, Khursheed A Malik",
        "year": 2003,
        "journal": "",
        "citations": 135,
        "url": "https://doi.org/10.1016/s0167-7012(02)00191-4"
    },
    {
        "title": "Responses to salt stress in the halophyte Plantago crassifolia (Plantaginaceae)",
        "authors": "Oscar Vicente, Monica Boscaiu, Miguel \u00c1ngel Naranjo, Elena Estrelles, Jos\u00e9 Mar\u0131\u0301a Bell\u00e9s, Pilar Soriano",
        "year": 2004,
        "journal": "",
        "citations": 134,
        "url": "https://doi.org/10.1016/j.jaridenv.2003.12.003"
    },
    {
        "title": "Deep Transcriptome Sequencing of Wild Halophyte Rice, Porteresia coarctata, Provides Novel Insights into the Salinity and Submergence Tolerance Factors",
        "authors": "R. Garg, M. Verma, S. Agrawal, R. Shankar, M. Majee, M. Jain",
        "year": 2013,
        "journal": "",
        "citations": 134,
        "url": "https://doi.org/10.1093/dnares/dst042"
    },
    {
        "title": "Chloroplast redox imbalance governs phenotypic plasticity: the \u201cgrand design of photosynthesis\u201d revisited",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 132,
        "url": ""
    },
    {
        "title": "Halomonas boliviensis sp. nov., an alkalitolerant, moderate halophile isolated from soil around a Bolivian hypersaline lake",
        "authors": "Jorge Quillaguam\u00e1n, Rajni Hatti-Kaul, Bo Mattiasson, Maria Teresa Alvarez, Osvaldo Delgado",
        "year": 2004,
        "journal": "",
        "citations": 132,
        "url": "https://doi.org/10.1099/ijs.0.02800-0"
    },
    {
        "title": "Survey of halophyte species in China",
        "authors": "Zhao Kefu, Fan Hai, I.A. Ungar",
        "year": 2002,
        "journal": "",
        "citations": 129,
        "url": "https://doi.org/10.1016/s0168-9452(02)00160-7"
    },
    {
        "title": "Poly(<i>\u03b2</i>-hydroxybutyrate) production by a moderate halophile,<i>Halomonas boliviensis</i>LC1 using starch hydrolysate as substrate",
        "authors": "J. Quillaguam\u00e1n, S. Hashim, F. Bento, B. Mattiasson, R. Hatti-Kaul",
        "year": 2005,
        "journal": "",
        "citations": 128,
        "url": "https://doi.org/10.1111/j.1365-2672.2005.02589.x"
    },
    {
        "title": "Enhanced salt stress tolerance of rice plants expressing a vacuolar H<sup>+</sup>\u2010ATPase subunit c1 (<i>SaVHAc1</i>) gene from the halophyte grass <i>Spartina alterniflora</i> L\u00f6isel",
        "authors": "Niranjan Baisakh, Mangu V. RamanaRao, Kanniah Rajasekaran, Prasanta Subudhi, Jaroslav Janda, David Galbraith, Cheryl Vanier, Andy Pereira",
        "year": 2012,
        "journal": "",
        "citations": 127,
        "url": "https://doi.org/10.1111/j.1467-7652.2012.00678.x"
    },
    {
        "title": "Arcobacter halophilus sp. nov., the first obligate halophile in the genus Arcobacter",
        "authors": "Stuart P. Donachie, John P. Bowman, Stephen L. W. On, Maqsudul Alam",
        "year": 2005,
        "journal": "",
        "citations": 126,
        "url": "https://doi.org/10.1099/ijs.0.63581-0"
    },
    {
        "title": "Metabolomics and network analysis reveal the potential metabolites and biological pathways involved in salinity tolerance of the halophyte Salvadora persica",
        "authors": "Asha Kumari, Asish Kumar Parida",
        "year": 2018,
        "journal": "",
        "citations": 125,
        "url": "https://doi.org/10.1016/j.envexpbot.2017.12.021"
    },
    {
        "title": "Subcellular localization and stress responses of superoxide dismutase isoforms from leaves in the C<sub>3</sub>\u2010CAM intermediate halophyte <i>Mesembryanthemum crystallinum</i> L.",
        "authors": "Z. Miszalski, I. \u015alesak, E. Niewiadomska, R. Baczek\u2010Kwinta, U. L\u00fcttge, R. Ratajczak",
        "year": 1998,
        "journal": "",
        "citations": 125,
        "url": "https://doi.org/10.1046/j.1365-3040.1998.00266.x"
    },
    {
        "title": "Analysis of protein solvent interactions in glucose dehydrogenase from the extreme halophile\n                    <i>Haloferax mediterranei</i>",
        "authors": "K. Linda Britton, Patrick J. Baker, Martin Fisher, Sergey Ruzheinikov, D. James Gilmour, Mar\u00eda-Jos\u00e9 Bonete, Juan Ferrer, Carmen Pire, Julia Esclapez, David W. Rice",
        "year": 2006,
        "journal": "",
        "citations": 123,
        "url": "https://doi.org/10.1073/pnas.0508854103"
    },
    {
        "title": "Complete Genome Sequence Analysis of Enterobacter sp. SA187, a Plant Multi-Stress Tolerance Promoting Endophytic Bacterium",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 121,
        "url": ""
    },
    {
        "title": "Interactive effects of NaCl salinity and elevated atmospheric CO2 concentration on growth, photosynthesis, water relations and chemical composition of the potential cash crop halophyte Aster tripolium L.",
        "authors": "N. Geissler, S. Hussin, H.-W. Koyro",
        "year": 2009,
        "journal": "",
        "citations": 121,
        "url": "https://doi.org/10.1016/j.envexpbot.2008.11.001"
    },
    {
        "title": "Phenolic content, antioxidant, anti-inflammatory and anticancer activities of the edible halophyte Suaeda fruticosa Forssk",
        "authors": "Samia Oueslati, Riadh Ksouri, Hanen Falleh, Andr\u00e9 Pichette, Chedly Abdelly, Jean Legault",
        "year": 2012,
        "journal": "",
        "citations": 120,
        "url": "https://doi.org/10.1016/j.foodchem.2011.11.072"
    },
    {
        "title": "Isolation of Endophytic Plant Growth-Promoting Bacteria Associated with the Halophyte Salicornia europaea and Evaluation of their Promoting Activity Under Salt Stress",
        "authors": "Shuai Zhao, Na Zhou, Zheng-Yong Zhao, Ke Zhang, Guo-Hua Wu, Chang-Yan Tian",
        "year": 2016,
        "journal": "",
        "citations": 119,
        "url": "https://doi.org/10.1007/s00284-016-1096-7"
    },
    {
        "title": "Co-production of biochar, bio-oil and syngas from halophyte grass (Achnatherum splendens L.) under three different pyrolysis temperatures",
        "authors": "Muhammad Irfan, Qun Chen, Yan Yue, Renzhong Pang, Qimei Lin, Xiaorong Zhao, Hao Chen",
        "year": 2016,
        "journal": "",
        "citations": 119,
        "url": "https://doi.org/10.1016/j.biortech.2016.03.077"
    },
    {
        "title": "NACs, generalist in plant life",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 117,
        "url": ""
    },
    {
        "title": "Salt-induced photoinhibition of PSII is alleviated in halophyte Thellungiella halophila by increases of unsaturated fatty acids in membrane lipids",
        "authors": "Na Sui, Guoliang Han",
        "year": 2014,
        "journal": "",
        "citations": 117,
        "url": "https://doi.org/10.1007/s11738-013-1477-5"
    },
    {
        "title": "Improved drought and salt stress tolerance in transgenic tobacco overexpressing a novel A20/AN1 zinc-finger \u201cAlSAP\u201d gene isolated from the halophyte grass Aeluropus littoralis",
        "authors": "Rania Ben Saad, Nabil Zouari, Walid Ben Ramdhan, Jalel Azaza, Donaldo Meynard, Emmanuel Guiderdoni, Afif Hassairi",
        "year": 2009,
        "journal": "",
        "citations": 117,
        "url": "https://doi.org/10.1007/s11103-009-9560-4"
    },
    {
        "title": "Diversity of Bacterial Microbiota of Coastal Halophyte Limonium sinense and Amelioration of Salinity Stress Damage by Symbiotic Plant Growth-Promoting Actinobacterium Glutamicibacter halophytocola KLBMP 5180",
        "authors": "Sheng Qin, Wei-Wei Feng, Yue-Ji Zhang, Tian-Tian Wang, You-Wei Xiong, Ke Xing",
        "year": 2018,
        "journal": "",
        "citations": 117,
        "url": "https://doi.org/10.1128/aem.01533-18"
    },
    {
        "title": "Bioprospecting desert plant Bacillus endophytic strains for their potential to enhance plant stress tolerance",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 115,
        "url": ""
    },
    {
        "title": "Growth promotion of the seawater-irrigated oilseed halophyte Salicornia bigelovii inoculated with mangrove rhizosphere bacteria and halotolerant Azospirillum spp.",
        "authors": "Y. Bashan, M. Moreno, E. Troyo",
        "year": 2000,
        "journal": "",
        "citations": 115,
        "url": "https://doi.org/10.1007/s003740000246"
    },
    {
        "title": "Proteomics with a pinch of salt: A cyanobacterial perspective",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 114,
        "url": ""
    },
    {
        "title": "Characterization and expression of a vacuolar Na+/H+ antiporter gene from the monocot halophyte Aeluropus littoralis",
        "authors": "Gao-Hua Zhang, Qiao Su, Li-Jia An, Song Wu",
        "year": 2008,
        "journal": "",
        "citations": 114,
        "url": "https://doi.org/10.1016/j.plaphy.2007.10.022"
    },
    {
        "title": "Assessing the effect of pyrolysis temperature on the molecular properties and copper sorption capacity of a halophyte biochar",
        "authors": "Jing Wei, Chen Tu, Guodong Yuan, Ying Liu, Dongxue Bi, Liang Xiao, Jian Lu, Benny K.G. Theng, Hailong Wang, Lijuan Zhang, Xiangzhi Zhang",
        "year": 2019,
        "journal": "",
        "citations": 114,
        "url": "https://doi.org/10.1016/j.envpol.2019.04.128"
    },
    {
        "title": "Plant-Growth-Promoting Bacteria Mitigating Soil Salinity Stress in Plants",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 113,
        "url": ""
    },
    {
        "title": "Salt tolerance in the halophyte Salicornia dolichostachya Moss: Growth, morphology and physiology",
        "authors": "Diana Katschnig, Rob Broekman, Jelte Rozema",
        "year": 2013,
        "journal": "",
        "citations": 113,
        "url": "https://doi.org/10.1016/j.envexpbot.2012.04.002"
    },
    {
        "title": "Induction of Crassulacean Acid Metabolism in the Facultative Halophyte <i>Mesembryanthemum crystallinum</i> by Abscisic Acid",
        "authors": "Chun Chu, Ziyu Dai, Maurice S. B. Ku, Gerald E. Edwards",
        "year": 1990,
        "journal": "",
        "citations": 112,
        "url": "https://doi.org/10.1104/pp.93.3.1253"
    },
    {
        "title": "Mucilage and polysaccharides in the halophyte plant species Kosteletzkya virginica: Localization and composition in relation to salt stress",
        "authors": "Michel Edmond Ghanem, Rui-Ming Han, Birgit Classen, Jo\u00eblle Quetin-Leclerq, Gregory Mahy, Cheng-Jiang Ruan, Pei Qin, Francisco P\u00e9rez-Alfocea, Stanley Lutts",
        "year": 2010,
        "journal": "",
        "citations": 112,
        "url": "https://doi.org/10.1016/j.jplph.2009.10.012"
    },
    {
        "title": "Salt Tolerance in the Halophyte<i>Suaeda maritima</i>L. Dum.: Evaluation of the Effect of Salinity upon Growth",
        "authors": "A. R. YEO, T. J. FLOWERS",
        "year": 1980,
        "journal": "",
        "citations": 110,
        "url": "https://doi.org/10.1093/jxb/31.4.1171"
    },
    {
        "title": "Different antioxidant defense responses to salt stress during germination and vegetative stages of endemic halophyte Gypsophila oblanceolata Bark.",
        "authors": "Askim Hediye Sekmen, Ismail Turkan, Zehra Ozgecan Tanyolac, Ceyda Ozfidan, Ahmet Dinc",
        "year": 2012,
        "journal": "",
        "citations": 110,
        "url": "https://doi.org/10.1016/j.envexpbot.2011.10.012"
    },
    {
        "title": "Over-expression of the Peroxisomal Ascorbate Peroxidase (SbpAPX) Gene Cloned from Halophyte Salicornia brachiata Confers Salt and Drought Stress Tolerance in Transgenic Tobacco",
        "authors": "Natwar Singh, Avinash Mishra, Bhavanath Jha",
        "year": 2013,
        "journal": "",
        "citations": 107,
        "url": "https://doi.org/10.1007/s10126-013-9548-6"
    },
    {
        "title": "The effects of salt stress on growth, water relations and ion accumulation in two halophyte Atriplex species",
        "authors": "O. Belkheiri, M. Mulas",
        "year": 2013,
        "journal": "",
        "citations": 105,
        "url": "https://doi.org/10.1016/j.envexpbot.2011.07.001"
    },
    {
        "title": "Physiological, Anatomical and Metabolic Implications of Salt Tolerance in the Halophyte Salvadora persica under Hydroponic Culture Condition",
        "authors": "Asish K. Parida, Sairam K. Veerabathini, Asha Kumari, Pradeep K. Agarwal",
        "year": 2016,
        "journal": "",
        "citations": 105,
        "url": "https://doi.org/10.3389/fpls.2016.00351"
    },
    {
        "title": "Role and Functional Differences of HKT1-Type Transporters in Plants under Salt Stress",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 104,
        "url": ""
    },
    {
        "title": "The SbMT-2 Gene from a Halophyte Confers Abiotic Stress Tolerance and Modulates ROS Scavenging in Transgenic Tobacco",
        "authors": "Amit Kumar Chaturvedi, Manish Kumar Patel, Avinash Mishra, Vivekanand Tiwari, Bhavanath Jha",
        "year": 2014,
        "journal": "",
        "citations": 104,
        "url": "https://doi.org/10.1371/journal.pone.0111379"
    },
    {
        "title": "Germination of Dimorphic Seeds of the Desert Annual Halophyte Suaeda aralocaspica (Chenopodiaceae), a C4 Plant without Kranz Anatomy",
        "authors": "Lei Wang, Zhenying Huang, Carol C. Baskin, Jerry M. Baskin, Ming Dong",
        "year": 2008,
        "journal": "",
        "citations": 104,
        "url": "https://doi.org/10.1093/aob/mcn158"
    },
    {
        "title": "Induced growth promotion and higher salt tolerance in the halophyte grass Puccinellia tenuiflora by beneficial rhizobacteria",
        "authors": "Shu-Qi Niu, Hui-Ru Li, Paul W. Par\u00e9, Mina Aziz, Suo-Min Wang, Huazhong Shi, Jing Li, Qing-Qing Han, Shi-Qian Guo, Jian Li, Qiang Guo, Qing Ma, Jin-Lin Zhang",
        "year": 2015,
        "journal": "",
        "citations": 104,
        "url": "https://doi.org/10.1007/s11104-015-2767-z"
    },
    {
        "title": "Physiological and proteomic analyses of salt stress response in the halophyte <scp><i>H</i></scp><i>alogeton glomeratus</i>",
        "authors": "JUNCHENG WANG, YAXIONG MENG, BAOCHUN LI, XIAOLE MA, YONG LAI, ERJING SI, KE YANG, XIANLIANG XU, XUNWU SHANG, HUAJUN WANG, DI WANG",
        "year": 2014,
        "journal": "",
        "citations": 104,
        "url": "https://doi.org/10.1111/pce.12428"
    },
    {
        "title": "Regulation of osmoadaptation in the moderate halophile Halobacillus halophilus: chloride, glutamate and switching osmolyte strategies",
        "authors": "Stephan H Saum, Volker M\u00fcller",
        "year": 2008,
        "journal": "",
        "citations": 103,
        "url": "https://doi.org/10.1186/1746-1448-4-4"
    },
    {
        "title": "The effect of extended exposure to hypersaline conditions on the germination of five inland halophyte species",
        "authors": "Carolyn Howes Keiffer, Irwin A. Ungar",
        "year": 1997,
        "journal": "",
        "citations": 103,
        "url": "https://doi.org/10.2307/2445887"
    },
    {
        "title": "Seed Germination and Radicle Growth of a Halophyte, Kalidium caspicum(Chenopodiaceae)",
        "authors": "K Tobe",
        "year": 2000,
        "journal": "",
        "citations": 102,
        "url": "https://doi.org/10.1006/anbo.1999.1077"
    },
    {
        "title": "Does salt stress lead to increased susceptibility of photosystem II to photoinhibition and changes in photosynthetic pigment composition in halophyte Suaeda salsa grown outdoors?",
        "authors": "Congming Lu, Nianwei Qiu, Qingtao Lu, Baoshan Wang, Tingyun Kuang",
        "year": 2002,
        "journal": "",
        "citations": 102,
        "url": "https://doi.org/10.1016/s0168-9452(02)00281-9"
    },
    {
        "title": "Solvent effects on phenolic contents and biological activities of the halophyte Limoniastrum monopetalum leaves",
        "authors": "Najla Trabelsi, Wided Megdiche, Riadh Ksouri, Hanen Falleh, Samia Oueslati, Bourgou Soumaya, Hafedh Hajlaoui, Chedly Abdelly",
        "year": 2010,
        "journal": "",
        "citations": 102,
        "url": "https://doi.org/10.1016/j.lwt.2009.11.003"
    },
    {
        "title": "In vitro screening of elastase, collagenase, hyaluronidase, and tyrosinase inhibitory and antioxidant activities of 22 halophyte plant extracts for novel cosmeceuticals",
        "authors": "Chanipa Jiratchayamaethasakul, Yuling Ding, Ouibo Hwang, Seung-Tae Im, Yebin Jang, Seung-Won Myung, Jeong Min Lee, Hyun-Soo Kim, Seok-Chun Ko, Seung-Hong Lee",
        "year": 2020,
        "journal": "",
        "citations": 102,
        "url": "https://doi.org/10.1186/s41240-020-00149-8"
    },
    {
        "title": "Bacillus mycoides PM35 Reinforces Photosynthetic Efficiency, Antioxidant Defense, Expression of Stress-Responsive Genes, and Ameliorates the Effects of Salinity Stress in Maize",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 101,
        "url": ""
    },
    {
        "title": "Genome-Wide Analysis of Gene Expression Provides New Insights into Cold Responses in Thellungiella salsuginea",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 100,
        "url": ""
    },
    {
        "title": "Marinobacter lipolyticus sp. nov., a novel moderate halophile with lipolytic activity",
        "authors": "S. Mart\u00edn, M. C. M\u00e1rquez, C. S\u00e1nchez-Porro, E. Mellado, D. R. Arahal, A. Ventosa",
        "year": 2003,
        "journal": "",
        "citations": 100,
        "url": "https://doi.org/10.1099/ijs.0.02528-0"
    },
    {
        "title": "Genetic engineering of glycine betaine biosynthesis to enhance abiotic stress tolerance in plants",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 99,
        "url": ""
    },
    {
        "title": "Halotolerant Plant Growth-Promoting Rhizobacteria Isolated From Saline Soil Improve Nitrogen Fixation and Alleviate Salt Stress in Rice Plants",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 99,
        "url": ""
    },
    {
        "title": "Interactive effects of various salt and alkali stresses on growth, organic solutes, and cation accumulation in a halophyte Spartina alterniflora (Poaceae)",
        "authors": "R. Li, F. Shi, K. Fukuda",
        "year": 2010,
        "journal": "",
        "citations": 99,
        "url": "https://doi.org/10.1016/j.envexpbot.2009.10.004"
    },
    {
        "title": "Effects of sodium chloride treatments on growth and ion accumulation of the halophyte <i>Haloxylon recurvum</i>",
        "authors": "M. Ajmal Khan, Irwin A. Ungar, Allan M. Showalter",
        "year": 2000,
        "journal": "",
        "citations": 99,
        "url": "https://doi.org/10.1080/00103620009370625"
    },
    {
        "title": "Halophyte filter beds for treatment of saline wastewater from aquaculture",
        "authors": "J.M. Webb, R. Quint\u00e3, S. Papadimitriou, L. Norman, M. Rigby, D.N. Thomas, L. Le Vay",
        "year": 2012,
        "journal": "",
        "citations": 98,
        "url": "https://doi.org/10.1016/j.watres.2012.06.034"
    },
    {
        "title": "Differential Activity of Plasma and Vacuolar Membrane Transporters Contributes to Genotypic Differences in Salinity Tolerance in a Halophyte Species, Chenopodium quinoa",
        "authors": "Edgar Bonales-Alatorre, Igor Pottosin, Lana Shabala, Zhong-Hua Chen, Fanrong Zeng, Sven-Erik Jacobsen, Sergey Shabala",
        "year": 2013,
        "journal": "",
        "citations": 97,
        "url": "https://doi.org/10.3390/ijms14059267"
    },
    {
        "title": "Population ecology of halophyte seeds",
        "authors": "Irwin A. Ungar",
        "year": 1987,
        "journal": "",
        "citations": 96,
        "url": "https://doi.org/10.1007/bf02858320"
    },
    {
        "title": "Molecular Cloning and Characterization of a Vacuolar H+-pyrophos-phatase Gene, SsVP, from the Halophyte Suaeda salsa and its Overexpression Increases Salt and Drought Tolerance of Arabidopsis",
        "authors": "Shanli Guo, Haibo Yin, Xia Zhang, Fengyun Zhao, Pinghua Li, Shihua Chen, Yanxiu Zhao, Hui Zhang",
        "year": 2006,
        "journal": "",
        "citations": 96,
        "url": "https://doi.org/10.1007/s11103-005-2417-6"
    },
    {
        "title": "Distinct responses to copper stress in the halophyte <i>Mesembryanthemum crystallinum</i>",
        "authors": "John C. Thomas, Farah K. Malick, Charles Endreszl, Elizabeth C. Davies, Kent S. Murray",
        "year": 1998,
        "journal": "",
        "citations": 95,
        "url": "https://doi.org/10.1034/j.1399-3054.1998.1020304.x"
    },
    {
        "title": "Photosynthesis and Pigments Influenced By Light Intensity and Salinity in the Halophile<i>Dunaliella Salina</i>(Chlorophyta)",
        "authors": "Laurel A. Loeblich",
        "year": 1982,
        "journal": "",
        "citations": 94,
        "url": "https://doi.org/10.1017/s0025315400019706"
    },
    {
        "title": "Cloning and transcript analysis of type 2 metallothionein gene (SbMT-2) from extreme halophyte Salicornia brachiata and its heterologous expression in E. coli",
        "authors": "Amit Kumar Chaturvedi, Avinash Mishra, Vivekanand Tiwari, Bhavanath Jha",
        "year": 2012,
        "journal": "",
        "citations": 94,
        "url": "https://doi.org/10.1016/j.gene.2012.03.001"
    },
    {
        "title": "NaCl enhances thylakoid-bound SOD activity in the leaves of C3 halophyte Suaeda salsa L.",
        "authors": "Zhang Qiu-Fang, Li Yuan-Yuan, Pang Cai-Hong, Lu Cong-Ming, Wang Bao-Shan",
        "year": 2005,
        "journal": "",
        "citations": 93,
        "url": "https://doi.org/10.1016/j.plantsci.2004.09.002"
    },
    {
        "title": "Characterization of a DRE-binding transcription factor from a halophyte Atriplex hortensis",
        "authors": "Yi-Guo Shen, Wan-Ke Zhang, Dong-Qing Yan, Bao-Xing Du, Jin-Song Zhang, Qiang Liu, Shou-Yi Chen",
        "year": 2003,
        "journal": "",
        "citations": 93,
        "url": "https://doi.org/10.1007/s00122-003-1226-z"
    },
    {
        "title": "A salt-inducible chloroplastic monodehydroascorbate reductase from halophyte Avicennia marina confers salt stress tolerance on transgenic plants",
        "authors": "Kumaresan Kavitha, Suja George, Gayatri Venkataraman, Ajay Parida",
        "year": 2010,
        "journal": "",
        "citations": 92,
        "url": "https://doi.org/10.1016/j.biochi.2010.06.009"
    },
    {
        "title": "Expression of the cation transporter McHKT1 in a halophyte",
        "authors": "Hua Su, Enrique Balderas, Rosario Vera-Estrella, Dortje Golldack, Francoise Quigley, Chengsong Zhao, Omar Pantoja, Hans J. Bohnert",
        "year": 2003,
        "journal": "",
        "citations": 92,
        "url": "https://doi.org/10.1023/a:1025445612244"
    },
    {
        "title": "The response of plasma membrane lipid composition in callus of the halophyte <i>Spartina patens</i> (Poaceae) to salinity stress",
        "authors": "Jinglan Wu, Denise M. Seliskar, John L. Gallagher",
        "year": 2005,
        "journal": "",
        "citations": 92,
        "url": "https://doi.org/10.3732/ajb.92.5.852"
    },
    {
        "title": "Sustainable agricultural management of saline soils in arid and semi-arid Mediterranean regions through halophytes, microbial and soil-based technologies",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 91,
        "url": ""
    },
    {
        "title": "SsHKT1;1 is a potassium transporter of the C3 halophyte Suaeda salsa that is involved in salt tolerance",
        "authors": "Qun Shao, Ning Han, Tonglou Ding, Feng Zhou, Baoshan Wang",
        "year": 2014,
        "journal": "",
        "citations": 91,
        "url": "https://doi.org/10.1071/fp13265"
    },
    {
        "title": "Comparison of the effects of salt-stress and alkali-stress on photosynthesis and energy storage of an alkali-resistant halophyte Chloris virgata",
        "authors": "C. W. Yang, A. Jianaer, C. Y. Li, D. C. Shi, D. L. Wang",
        "year": 2008,
        "journal": "",
        "citations": 91,
        "url": "https://doi.org/10.1007/s11099-008-0047-3"
    },
    {
        "title": "Effect of Temperature, Light and Salinity on Seed Germination and Radicle Growth of the Geographically Widespread Halophyte Shrub Halocnemum strobilaceum",
        "authors": "X.-X. Qu, Z.-Y. Huang, J. M. Baskin, C. C. Baskin",
        "year": 2007,
        "journal": "",
        "citations": 91,
        "url": "https://doi.org/10.1093/aob/mcm047"
    },
    {
        "title": "Introgression of the SbASR-1 Gene Cloned from a Halophyte Salicornia brachiata Enhances Salinity and Drought Endurance in Transgenic Groundnut (Arachis hypogaea) and Acts as a Transcription Factor",
        "authors": "Vivekanand Tiwari, Amit Kumar Chaturvedi, Avinash Mishra, Bhavanath Jha",
        "year": 2015,
        "journal": "",
        "citations": 91,
        "url": "https://doi.org/10.1371/journal.pone.0131567"
    },
    {
        "title": "Salt regulation of transcript levels for the c subunit of a leaf vacuolar H<sup>+</sup>\u2010ATPase in the halophyte <i>Mesembryanthemum crystallinum</i>",
        "authors": "Miltos S. Tsiantis, Dolores M. Bartholomew, J. Andrew C. Smith",
        "year": 1996,
        "journal": "",
        "citations": 91,
        "url": "https://doi.org/10.1046/j.1365-313x.1996.9050729.x"
    },
    {
        "title": "Coordinate up-regulation of V-H+-ATPase and vacuolar Na+/H+ antiporter as a response to NaCl treatment in a C3 halophyte Suaeda salsa",
        "authors": "Nianwei Qiu, Min Chen, Jianrong Guo, Huayin Bao, Xiuling Ma, Baoshan Wang",
        "year": 2007,
        "journal": "",
        "citations": 89,
        "url": "https://doi.org/10.1016/j.plantsci.2007.02.013"
    },
    {
        "title": "Genome Structures and Halophyte-Specific Gene Expression of the Extremophile\n                    <i>Thellungiella parvula</i>\n                    in Comparison with\n                    <i>Thellungiella salsuginea</i>\n                    (\n                    <i>Thellungiella halophila</i>\n                    ) and Arabidopsis",
        "authors": "Dong-Ha Oh, Maheshi Dassanayake, Jeffrey S. Haas, Anna Kropornika, Chris Wright, Matilde Paino d\u2019Urzo, Hyewon Hong, Shahjahan Ali, Alvaro Hernandez, Georgina M. Lambert, Gunsu Inan, David W. Galbraith, Ray A. Bressan, Dae-Jin Yun, Jian-Kang Zhu, John M. Cheeseman, Hans J. Bohnert",
        "year": 2010,
        "journal": "",
        "citations": 89,
        "url": "https://doi.org/10.1104/pp.110.163923"
    },
    {
        "title": "Plant volatiles in extreme terrestrial and marine environments",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 86,
        "url": ""
    },
    {
        "title": "Isolation and Characterization of Salt-sensitive Mutants of the Moderate Halophile Halomonas elongata and Cloning of the Ectoine Synthesis Genes",
        "authors": "David C\u00e1novas, Carmen Vargas, Fernando Iglesias-Guerra, Laszlo N. Csonka, David Rhodes, Antonio Ventosa, Joaqu\u0131\u0301n J. Nieto",
        "year": 1997,
        "journal": "",
        "citations": 86,
        "url": "https://doi.org/10.1074/jbc.272.41.25794"
    },
    {
        "title": "Maritime Halophyte Species from Southern Portugal as Sources of Bioactive Molecules",
        "authors": "Maria Rodrigues, Katkam Gangadhar, Catarina Vizetto-Duarte, Sileshi Wubshet, Nils Nyberg, Lu\u00edsa Barreira, Jo\u00e3o Varela, Lu\u00edsa Cust\u00f3dio",
        "year": 2014,
        "journal": "",
        "citations": 86,
        "url": "https://doi.org/10.3390/md12042228"
    },
    {
        "title": "The effect of sodium chloride on enzyme activities from four halophyte species of chenopodiaceae",
        "authors": "T.J. Flowers",
        "year": 1972,
        "journal": "",
        "citations": 85,
        "url": "https://doi.org/10.1016/s0031-9422(00)90147-x"
    },
    {
        "title": "Primary responses to salt stress in a halophyte, smooth cordgrass (Spartina alterniflora Loisel.)",
        "authors": "Niranjan Baisakh, Prasanta K. Subudhi, Pritish Varadwaj",
        "year": 2008,
        "journal": "",
        "citations": 85,
        "url": "https://doi.org/10.1007/s10142-008-0075-x"
    },
    {
        "title": "HKT sodium and potassium transporters in <i>Arabidopsis thaliana</i> and related halophyte species",
        "authors": "Akhtar Ali, Natalia Raddatz, Jose M. Pardo, Dae\u2010Jin Yun",
        "year": 2020,
        "journal": "",
        "citations": 85,
        "url": "https://doi.org/10.1111/ppl.13166"
    },
    {
        "title": "Improved growth and salinity tolerance of the halophyte Salicornia sp. by co\u2013inoculation with endophytic and rhizosphere bacteria",
        "authors": "Behzad Razzaghi Komaresofla, Hossein Ali Alikhani, Hassan Etesami, Nayer Azam Khoshkholgh-Sima",
        "year": 2019,
        "journal": "",
        "citations": 85,
        "url": "https://doi.org/10.1016/j.apsoil.2019.02.022"
    },
    {
        "title": "Physiological responses of the halophyte Sesuvium portulacastrum to salt stress and their relevance for saline soil bio-reclamation",
        "authors": "Niramaya S. Muchate, Ganesh C. Nikalje, Nilima S. Rajurkar, P. Suprasanna, Tukaram D. Nikam",
        "year": 2016,
        "journal": "",
        "citations": 85,
        "url": "https://doi.org/10.1016/j.flora.2016.07.009"
    },
    {
        "title": "Enhanced thermotolerance of photosystem\ufffdII in salt-adapted plants of the halophyte Artemisia anethifolia",
        "authors": "Xiaogang Wen, Nianwei Qiu, Qingtao Lu, Congming Lu",
        "year": 2004,
        "journal": "",
        "citations": 84,
        "url": "https://doi.org/10.1007/s00425-004-1382-7"
    },
    {
        "title": "Constitutive high-level SOS1 expression and absence of HKT1;1 expression in the salt-accumulating halophyte Salicornia dolichostachya",
        "authors": "D. Katschnig, T. Bliek, J. Rozema, H. Schat",
        "year": 2015,
        "journal": "",
        "citations": 84,
        "url": "https://doi.org/10.1016/j.plantsci.2015.02.011"
    },
    {
        "title": "Accumulation of heavy metals and its biochemical responses in<i>Salicornia brachiata</i>, an extreme halophyte",
        "authors": "Anubha Sharma, Iti Gontia, Pradeep K. Agarwal, Bhavanath Jha",
        "year": 2010,
        "journal": "",
        "citations": 84,
        "url": "https://doi.org/10.1080/17451000903434064"
    },
    {
        "title": "Unravelling the antioxidant potential and the phenolic composition of different anatomical organs of the marine halophyte Limonium algarvense",
        "authors": "Maria Jo\u00e3o Rodrigues, Ambre Soszynski, Alice Martins, Am\u00e9lia P. Rauter, Nuno R. Neng, Jos\u00e9 M.F. Nogueira, Jo\u00e3o Varela, Lu\u00edsa Barreira, Lu\u00edsa Cust\u00f3dio",
        "year": 2015,
        "journal": "",
        "citations": 84,
        "url": "https://doi.org/10.1016/j.indcrop.2015.08.061"
    },
    {
        "title": "Poly(\u03b2-hydroxybutyrate) production by a moderate halophile, Halomonas boliviensis LC1",
        "authors": "Jorge Quillaguam\u00e1n, Osvaldo Delgado, Bo Mattiasson, Rajni Hatti-Kaul",
        "year": 2006,
        "journal": "",
        "citations": 83,
        "url": "https://doi.org/10.1016/j.enzmictec.2005.05.013"
    },
    {
        "title": "Ameliorative Impact of an Extract of the Halophyte Arthrocnemum macrostachyum on Growth and Biochemical Parameters of Soybean Under Salinity Stress",
        "authors": "Mahmoud S. Osman, Ali A. Badawy, Ahmed I. Osman, Arafat Abdel Hamed Abdel Latef",
        "year": 2020,
        "journal": "",
        "citations": 83,
        "url": "https://doi.org/10.1007/s00344-020-10185-2"
    },
    {
        "title": "Plant growth-promoting effect and genomic analysis of the beneficial endophyte Streptomyces sp. KLBMP 5084 isolated from halophyte Limonium sinense",
        "authors": "Sheng Qin, Wei-Wei Feng, Tian-Tian Wang, Peng Ding, Ke Xing, Ji-Hong Jiang",
        "year": 2017,
        "journal": "",
        "citations": 83,
        "url": "https://doi.org/10.1007/s11104-017-3192-2"
    },
    {
        "title": "Searching for new sources of innovative products for the food industry within halophyte aromatic plants: In\u00a0vitro antioxidant activity and phenolic and mineral contents of infusions and decoctions of Crithmum maritimum L.",
        "authors": "Catarina Guerreiro Pereira, Lu\u00edsa Barreira, Nuno da Rosa Neng, Jos\u00e9 Manuel Flor\u00eancio Nogueira, C\u00e1tia Marques, Tam\u00e1ra F. Santos, Jo\u00e3o Varela, Lu\u00edsa Cust\u00f3dio",
        "year": 2017,
        "journal": "",
        "citations": 83,
        "url": "https://doi.org/10.1016/j.fct.2017.04.018"
    },
    {
        "title": "Erythrobacter flavus sp. nov., a slight halophile from the East Sea in Korea",
        "authors": "Jung-Hoon Yoon, Hongik Kim, In-Gi Kim, Kook Hee Kang, Yong-Ha Park",
        "year": 2003,
        "journal": "",
        "citations": 82,
        "url": "https://doi.org/10.1099/ijs.0.02510-0"
    },
    {
        "title": "Salt tolerance of a cash crop halophyte Suaeda fruticosa: biochemical responses to salt and exogenous chemical treatments",
        "authors": "Abdul Hameed, Tabassum Hussain, Salman Gulzar, Irfan Aziz, Bilquees Gul, M. Ajmal Khan",
        "year": 2012,
        "journal": "",
        "citations": 81,
        "url": "https://doi.org/10.1007/s11738-012-1035-6"
    },
    {
        "title": "Assessing the role of endophytic bacteria in the halophyte <i>Arthrocnemum macrostachyum</i> salt tolerance",
        "authors": "S. Navarro\u2010Torre, J. M. Barcia\u2010Piedras, E. Mateos\u2010Naranjo, S. Redondo\u2010G\u00f3mez, M. Camacho, M. A. Caviedes, E. Pajuelo, I. D. Rodr\u00edguez\u2010Llorente",
        "year": 2016,
        "journal": "",
        "citations": 81,
        "url": "https://doi.org/10.1111/plb.12521"
    },
    {
        "title": "Illumina-Based Analysis of Endophytic and Rhizosphere Bacterial Diversity of the Coastal Halophyte Messerschmidia sibirica",
        "authors": "Xue-Ying Tian, Cheng-Sheng Zhang",
        "year": 2017,
        "journal": "",
        "citations": 80,
        "url": "https://doi.org/10.3389/fmicb.2017.02288"
    },
    {
        "title": "Developing Transgenic Jatropha Using the SbNHX1 Gene from an Extreme Halophyte for Cultivation in Saline Wasteland",
        "authors": "Bhavanath Jha, Avinash Mishra, Anupama Jha, Mukul Joshi",
        "year": 2013,
        "journal": "",
        "citations": 80,
        "url": "https://doi.org/10.1371/journal.pone.0071136"
    },
    {
        "title": "Impact of soil salinity on the microbial structure of halophyte rhizosphere microbiome",
        "authors": "Salma Mukhtar, Babur Saeed Mirza, Samina Mehnaz, Muhammad Sajjad Mirza, Joan Mclean, Kauser Abdulla Malik",
        "year": 2018,
        "journal": "",
        "citations": 80,
        "url": "https://doi.org/10.1007/s11274-018-2509-5"
    },
    {
        "title": "Pathways of cadmium fluxes in the root of the halophyte Suaeda salsa",
        "authors": "Lianzhen Li, Xiaoli Liu, Willie J.G.M. Peijnenburg, Jianmin Zhao, Xiaobing Chen, Junbao Yu, Huifeng Wu",
        "year": 2012,
        "journal": "",
        "citations": 79,
        "url": "https://doi.org/10.1016/j.ecoenv.2011.09.007"
    },
    {
        "title": "Guard cell cation channels are involved in Na<sup>+</sup>\u2013induced stomatal closure in a halophyte",
        "authors": "Anne\u2010Ali\u00e9nor V\u00e9ry, Michael F. Robinson, Terry A. Mansfield, Dale Sanders",
        "year": 1998,
        "journal": "",
        "citations": 78,
        "url": "https://doi.org/10.1046/j.1365-313x.1998.00147.x"
    },
    {
        "title": "Efficient regulation of arsenic translocation to shoot tissue and modulation of phytochelatin levels and antioxidative defense system confers salinity and arsenic tolerance in the Halophyte Suaeda maritima",
        "authors": "Ashok Panda, Jaykumar Rangani, Asha Kumari, Asish Kumar Parida",
        "year": 2017,
        "journal": "",
        "citations": 78,
        "url": "https://doi.org/10.1016/j.envexpbot.2017.09.007"
    },
    {
        "title": "Salicylic acid differently impacts ethylene and polyamine synthesis in the glycophyte <i>Solanum lycopersicum</i> and the wild\u2010related halophyte <i>Solanum chilense</i> exposed to mild salt stress",
        "authors": "Emna Gharbi, Juan\u2010Pablo Mart\u00ednez, Hela Benahmed, Marie\u2010Laure Fauconnier, Stanley Lutts, Muriel Quinet",
        "year": 2016,
        "journal": "",
        "citations": 78,
        "url": "https://doi.org/10.1111/ppl.12458"
    },
    {
        "title": "The Vacuolar Na+/H+ Antiporter Gene SsNHX1 from the Halophyte Salsola soda Confers Salt Tolerance in Transgenic Alfalfa (Medicago sativa L.)",
        "authors": "Wangfeng Li, Deli Wang, Taicheng Jin, Qing Chang, Dongxu Yin, Shoumin Xu, Bao Liu, Lixia Liu",
        "year": 2010,
        "journal": "",
        "citations": 78,
        "url": "https://doi.org/10.1007/s11105-010-0224-y"
    },
    {
        "title": "Comparative Ni tolerance and accumulation potentials between Mesembryanthemum crystallinum (halophyte) and Brassica juncea: Metal accumulation, nutrient status and photosynthetic activity",
        "authors": "Taoufik Amari, Tahar Ghnaya, Ahmed Debez, Manel Taamali, Nabil Ben Youssef, Giorgio Lucchini, Gian Attilio Sacchi, Chedly Abdelly",
        "year": 2014,
        "journal": "",
        "citations": 78,
        "url": "https://doi.org/10.1016/j.jplph.2014.06.020"
    },
    {
        "title": "Interactive effects of salt and alkali stresses on seed germination, germination recovery, and seedling growth of a halophyte Spartina alterniflora (Poaceae)",
        "authors": "R. Li, F. Shi, K. Fukuda",
        "year": 2010,
        "journal": "",
        "citations": 78,
        "url": "https://doi.org/10.1016/j.sajb.2010.01.004"
    },
    {
        "title": "Antioxidant enzyme activities and hormonal status in\u00a0response to Cd stress in the wetland halophyte <i>Kosteletzkya virginica</i> under saline conditions",
        "authors": "Rui\u2010Ming Han, Isabelle Lef\u00e8vre, Alfonso Albacete, Francisco P\u00e9rez\u2010Alfocea, Gregorio Barba\u2010Esp\u00edn, Pedro D\u00edaz\u2010Vivancos, Muriel Quinet, Cheng\u2010Jiang Ruan, Jos\u00e9 Antonio Hern\u00e1ndez, Elena Cantero\u2010Navarro, Stanley Lutts",
        "year": 2012,
        "journal": "",
        "citations": 78,
        "url": "https://doi.org/10.1111/j.1399-3054.2012.01667.x"
    },
    {
        "title": "Seawater microorganisms have a high affinity glycine betaine uptake system which also recognizes dimethylsulfoniopropionate",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 77,
        "url": ""
    },
    {
        "title": "The Key Physiological Response to Alkali Stress by the Alkali\u2010Resistant Halophyte <i>Puccinellia tenuiflora</i> is the Accumulation of Large Quantities of Organic Acids and into the Rhyzosphere",
        "authors": "L. Q. Guo, D. C. Shi, D. L. Wang",
        "year": 2010,
        "journal": "",
        "citations": 77,
        "url": "https://doi.org/10.1111/j.1439-037x.2009.00397.x"
    },
    {
        "title": "Synthesis of salt-stable fluorescent nanoparticles (quantum dots) by polyextremophile halophilic bacteria",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 76,
        "url": ""
    },
    {
        "title": "Salt Stress Perception and Plant Growth Regulators in the Halophyte Mesembryanthemum crystallinum",
        "authors": "J. C. Thomas, H. J. Bohnert",
        "year": 1993,
        "journal": "",
        "citations": 76,
        "url": "https://doi.org/10.1104/pp.103.4.1299"
    },
    {
        "title": "NaCl increases the activity of the plasma membrane H+-ATPase in C3 halophyte Suaeda salsa callus",
        "authors": "Min Chen, Jie Song, Bao-Shan Wang",
        "year": 2009,
        "journal": "",
        "citations": 76,
        "url": "https://doi.org/10.1007/s11738-009-0371-7"
    },
    {
        "title": "How does NaCl improve tolerance to cadmium in the halophyte Sesuvium portulacastrum ?",
        "authors": "Wali Mariem, Ben Rjab Kilani, Guns\u00e9 Benet, Lakdhar Abdelbasset, Lutts Stanley, Poschenrieder Charlotte, Abdelly Chedly, Ghnaya Tahar",
        "year": 2014,
        "journal": "",
        "citations": 76,
        "url": "https://doi.org/10.1016/j.chemosphere.2014.07.041"
    },
    {
        "title": "Phylogenetic analysis of halophyte\u2010associated rhizobacteria and effect of halotolerant and halophilic phosphate\u2010solubilizing biofertilizers on maize growth under salinity stress conditions",
        "authors": "S. Mukhtar, M. Zareen, Z. Khaliq, S. Mehnaz, K.A. Malik",
        "year": 2019,
        "journal": "",
        "citations": 76,
        "url": "https://doi.org/10.1111/jam.14497"
    },
    {
        "title": "Enhancement of growth and salt tolerance of tomato seedlings by a natural halotolerant actinobacterium Glutamicibacter halophytocola KLBMP 5180 isolated from a coastal halophyte",
        "authors": "You-Wei Xiong, Yuan Gong, Xue-Wei Li, Pan Chen, Xiu-Yun Ju, Chun-Mei Zhang, Bo Yuan, Zuo-Peng Lv, Ke Xing, Sheng Qin",
        "year": 2019,
        "journal": "",
        "citations": 76,
        "url": "https://doi.org/10.1007/s11104-019-04310-8"
    },
    {
        "title": "Draft genome sequence of first monocot-halophytic species Oryza coarctata reveals stress-specific genes",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 75,
        "url": ""
    },
    {
        "title": "The effect of salt on protein synthesis in the halophyte Suaeda maritima",
        "authors": "J. L. Hall, T. J. Flowers",
        "year": 1973,
        "journal": "",
        "citations": 75,
        "url": "https://doi.org/10.1007/bf00387064"
    },
    {
        "title": "Ammonium nutrition in the halophyte Spartina alterniflora under salt stress: evidence for a priming effect of ammonium?",
        "authors": "Kamel Hessini, Karim Ben Hamed, Mhemmed Gandour, Maroua Mejri, Chedly Abdelly, Cristina Cruz",
        "year": 2013,
        "journal": "",
        "citations": 75,
        "url": "https://doi.org/10.1007/s11104-013-1616-1"
    },
    {
        "title": "HbCIPK2, a novel CBL\u2010interacting protein kinase from halophyte <i>Hordeum brevisubulatum</i>, confers salt and osmotic stress tolerance",
        "authors": "RUIFEN LI, JUNWEN ZHANG, GUANGYU WU, HONGZHI WANG, YAJUAN CHEN, JIANHUA WEI",
        "year": 2012,
        "journal": "",
        "citations": 75,
        "url": "https://doi.org/10.1111/j.1365-3040.2012.02511.x"
    },
    {
        "title": "Daily intake and the selection of feeding sitesby horses in heterogeneous wet grasslands",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 74,
        "url": ""
    },
    {
        "title": "Cd-induced growth reduction in the halophyte Sesuvium portulacastrum is significantly improved by NaCl",
        "authors": "Tahar Ghnaya, In\u00e8s Slama, Dorsaf Messedi, Claude Grignon, Mohamed Habib Ghorbel, Chedly Abdelly",
        "year": 2006,
        "journal": "",
        "citations": 74,
        "url": "https://doi.org/10.1007/s10265-006-0042-3"
    },
    {
        "title": "Changes in content and fatty acid profiles of total lipids and sulfolipids in the halophyte Crithmum maritimum under salt stress",
        "authors": "Karim Ben Hamed, Nabil Ben Youssef, Annamaria Ranieri, Mokhtar Zarrouk, Chedly Abdelly",
        "year": 2005,
        "journal": "",
        "citations": 74,
        "url": "https://doi.org/10.1016/j.jplph.2004.11.010"
    },
    {
        "title": "Salt tolerance of the annual halophyte Cakile maritima as affected by the provenance and the developmental stage",
        "authors": "Wided Megdiche, Nader Ben Amor, Ahmed Debez, Kamel Hessini, Riadh Ksouri, Yasmine Zuily-Fodil, Chedly Abdelly",
        "year": 2007,
        "journal": "",
        "citations": 74,
        "url": "https://doi.org/10.1007/s11738-007-0047-0"
    },
    {
        "title": "An endophytic bacterium isolated from roots of the halophyte Prosopis strombulifera produces ABA, IAA, gibberellins A1 and A3 and jasmonic acid in chemically-defined culture medium",
        "authors": "Patricia Piccoli, Claudia Travaglia, Ana Cohen, Laura Sosa, Paula Cornejo, Ricardo Masuelli, Rub\u00e9n Bottini",
        "year": 2010,
        "journal": "",
        "citations": 74,
        "url": "https://doi.org/10.1007/s10725-010-9536-z"
    },
    {
        "title": "Artisanal salt production in Aveiro/Portugal - an ecofriendly process",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 73,
        "url": ""
    },
    {
        "title": "Salt Tolerance in the Halophyte<i>Suaeda maritima</i>L. Dum.: Intracellular Compartmentation of Ions",
        "authors": "A. R. YEO",
        "year": 1981,
        "journal": "",
        "citations": 73,
        "url": "https://doi.org/10.1093/jxb/32.3.487"
    },
    {
        "title": "Betacyanin accumulation in the leaves of C3 halophyte Suaeda salsa L. is induced by watering roots with H2O2",
        "authors": "Chang-Quan Wang, Min Chen, Bao-Shan Wang",
        "year": 2007,
        "journal": "",
        "citations": 73,
        "url": "https://doi.org/10.1016/j.plantsci.2006.06.015"
    },
    {
        "title": "Isolation and characterization of endophytic bacteria colonizing halophyte and other salt tolerant plant species from coastal Gujarat",
        "authors": "Arora Sanjay, N. Patel Purvi, J. Vanza Meghna, G. Rao G.",
        "year": 2014,
        "journal": "",
        "citations": 73,
        "url": "https://doi.org/10.5897/ajmr2013.5557"
    },
    {
        "title": "European salt marshes diversity and functioning: The case study of the Mont Saint-Michel bay, France",
        "authors": "",
        "year": "",
        "journal": "",
        "citations": 72,
        "url": ""
    },
    {
        "title": "Sesuvium portulacastrum (L.) L. a promising halophyte: cultivation, utilization and distribution in India",
        "authors": "Vinayak Haribhau Lokhande, Tukaram Dayaram Nikam, Penna Suprasanna",
        "year": 2009,
        "journal": "",
        "citations": 72,
        "url": "https://doi.org/10.1007/s10722-009-9435-1"
    },
    {
        "title": "Leaf gas exchange and solute accumulation in the halophyte Salvadora persica grown at moderate salinity",
        "authors": "Albino Maggio, Muppala P Reddy, Robert J Joly",
        "year": 2000,
        "journal": "",
        "citations": 72,
        "url": "https://doi.org/10.1016/s0098-8472(00)00051-4"
    },
    {
        "title": "Metabolic profiling of cadmium-induced effects in one pioneer intertidal halophyte Suaeda salsa by NMR-based metabolomics",
        "authors": "Xiaoli Liu, Cuiyun Yang, Linbao Zhang, Lianzhen Li, Sujing Liu, Junbao Yu, Liping You, Di Zhou, Chuanhai Xia, Jianmin Zhao, Huifeng Wu",
        "year": 2011,
        "journal": "",
        "citations": 72,
        "url": "https://doi.org/10.1007/s10646-011-0699-9"
    },
    {
        "title": "Halobacillus karajensis sp. nov., a novel moderate halophile",
        "authors": "M. A. Amoozegar, F. Malekzadeh, K. A. Malik, P. Schumann, C. Spr\u00f6er",
        "year": 2003,
        "journal": "",
        "citations": 71,
        "url": "https://doi.org/10.1099/ijs.0.02448-0"
    },
    {
        "title": "Effects of salinity and ascorbic acid on growth, water status and antioxidant system in a perennial halophyte",
        "authors": "Abdul Hameed, Salman Gulzar, Irfan Aziz, Tabassum Hussain, Bilquees Gul, M. Ajmal Khan",
        "year": 2015,
        "journal": "",
        "citations": 71,
        "url": "https://doi.org/10.1093/aobpla/plv004"
    },
    {
        "title": "Photosynthetic limitations of a halophyte sea aster (Aster tripolium L) under water stress and NaCl stress",
        "authors": "Akihiro Ueda, Michio Kanechi, Yuichi Uno, Noboru Inagaki",
        "year": 2002,
        "journal": "",
        "citations": 71,
        "url": "https://doi.org/10.1007/s10265-002-0070-6"
    },
    {
        "title": "Single-cell-type quantitative proteomic and ionomic analysis of epidermal bladder cells from the halophyte model plant Mesembryanthemum crystallinum to identify salt-responsive proteins",
        "authors": "Bronwyn J. Barkla, Rosario Vera-Estrella, Carolyn Raymond",
        "year": 2016,
        "journal": "",
        "citations": 71,
        "url": "https://doi.org/10.1186/s12870-016-0797-1"
    },
    {
        "title": "Isolation, identification and expression analysis of salt-induced genes in Suaeda maritima, a natural halophyte, using PCR-based suppression subtractive hybridization",
        "authors": "Binod B Sahu, Birendra P Shaw",
        "year": 2009,
        "journal": "",
        "citations": 71,
        "url": "https://doi.org/10.1186/1471-2229-9-69"
    },
    {
        "title": "Endophytic and rhizosphere bacteria associated with the roots of the halophyte Salicornia europaea L. \u2013 community structure and metabolic potential",
        "authors": "Sonia Szyma\u0144ska, Tomasz P\u0142ociniczak, Zofia Piotrowska-Seget, Katarzyna Hrynkiewicz",
        "year": 2016,
        "journal": "",
        "citations": 71,
        "url": "https://doi.org/10.1016/j.micres.2016.05.012"
    }
];

    const table = new Tabulator("#most-cited-research-table", {
        data: tableData,
        layout: "fitColumns",
        pagination: "local",
        paginationSize: 15,
        movableColumns: true,
        columns: [
            {
                title: "Title",
                field: "title",
                formatter: function(cell) {
                    const val = cell.getValue();
                    const url = cell.getRow().getData().url;
                    if (url) {
                        return `<a href="${url}" target="_blank">${val}</a>`;
                    }
                    return val;
                },
                headerFilter: "input"
            },
            {
                title: "Authors",
                field: "authors",
                headerFilter: "input"
            },
            {
                title: "Year",
                field: "year",
                sorter: "number",
                headerFilter: "input"
            },
            {
                title: "Journal",
                field: "journal",
                headerFilter: "input"
            },
            {
                title: "Citations",
                field: "citations",
                sorter: "number",
                headerFilter: "input"
            }
        ]
    });

    // Download button
    document.getElementById("download-most-cited").addEventListener("click", function() {
        table.download("csv", "most_cited_research.csv");
    });
});

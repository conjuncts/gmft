
# test to_dict and from_dict



import copy
import json
import pytest
from gmft.pdf_bindings import BasePage
from gmft.auto import CroppedTable
from gmft.pdf_bindings.pdfium import PyPDFium2Document
from gmft.table_detection import RotatedCroppedTable
from gmft.table_function import TATRFormattedTable


@pytest.fixture(scope="session")
def doc_9():
    doc = PyPDFium2Document("test/samples/9.pdf")
    yield doc
    # cleanup
    doc.close()

def test_CroppedTable_to_dict(doc_tiny):
    # create a CroppedTable object
    page = doc_tiny[0]
    table = CroppedTable(page, (10, 10, 300, 300), 0.9, 0)
    table_dict = table.to_dict()
    assert table_dict == {
        'filename': "test/samples/tiny.pdf",
        'page_no': 0,
        'bbox': (10, 10, 300, 300),
        'confidence_score': 0.9,
        'label': 0
    }

def test_CroppedTable_from_dict(doc_tiny):
    # create a CroppedTable object
    page = doc_tiny[0]
    table = CroppedTable.from_dict({
        'filename': "test/samples/tiny.pdf",
        'page_no': 0,
        'bbox': (10, 10, 300, 150),
        'confidence_score': 0.9,
        'label': 0
    }, page)
    
    print(table.text())
    assert table.text() == """Simple document
Lorem ipsum dolor sit amet, consectetur adipiscing
Table 1. Selected Numbers"""


tiny_old_info = {
    "filename": "test/samples/tiny.pdf",
    "page_no": 0,
    "bbox": [76.66205596923828, 162.82687377929688, 440.9659729003906, 248.67056274414062],
    "confidence_score": 0.9996763467788696,
    "label": 0,
    "fctn_scale_factor": 2.0,
    "fctn_padding": [72,72,72,72],
    "config": {},
    "outliers": {},
    "fctn_results": {
        "scores": [
            0.9999045133590698,
            0.9998310804367065,
            0.9999147653579712,
            0.9998205304145813,
            0.9999688863754272,
            0.9998650550842285,
            0.9998096823692322,
            0.9897574186325073,
            0.9998759031295776
        ],
        "labels": [2,2,1,2,1,1,2,3,0],
        "boxes": [
            [71.36495971679688, 159.0726318359375, 797.0186767578125, 206.53753662109375],
            [70.94971466064453, 110.53954315185547, 797.128173828125, 158.9207000732422],
            [71.17463684082031, 73.58935546875, 329.6531677246094, 244.5222625732422],
            [71.1388931274414, 73.6107177734375, 797.3575439453125, 109.99236297607422],
            [331.3564147949219, 73.64269256591797, 576.944091796875, 244.3546905517578],
            [575.6424560546875, 73.62675476074219, 797.5115356445312, 244.22035217285156],
            [71.27164459228516, 206.5450439453125, 796.82958984375, 244.68435668945312],
            [71.13404083251953, 73.61981964111328, 797.3654174804688, 109.93215942382812],
            [71.12321472167969, 73.54254150390625, 797.08642578125, 244.42941284179688]
        ]
    }
}
def test_FormattedTable_from_dict_backcompat(doc_tiny):
    # create a CroppedTable object
    page = doc_tiny[0]
    formatted_table = TATRFormattedTable.from_dict(tiny_old_info, page)
    df = formatted_table.df()
    # get csv as string
    csv_str = df.to_csv(index=False, lineterminator='\n')
    
    assert csv_str == """Name,Celsius,Fahrenheit
Water Freezing Point,0,32
Water Boiling Point,100,212
Body Temperature,37,98.6
"""


def test_FormattedTable_to_dict_backcompat(doc_tiny):
    # assert that to_dict o from_dict is identity
    page = doc_tiny[0]
    dict2table = TATRFormattedTable.from_dict(tiny_old_info, page)
    dict2table2dict = dict2table.to_dict()
    
    assert dict2table2dict == tiny_info



tiny_info = {
    "filename": "test/samples/tiny.pdf",
    "page_no": 0,
    "bbox": [76.66205596923828, 162.82687377929688, 440.9659729003906, 248.67056274414062],
    "confidence_score": 0.9996763467788696,
    "label": 0,
    "config": {},
    "outliers": {},
    "fctn_results": {
        "scores": [
            0.9999045133590698,
            0.9998310804367065,
            0.9999147653579712,
            0.9998205304145813,
            0.9999688863754272,
            0.9998650550842285,
            0.9998096823692322,
            0.9897574186325073,
            0.9998759031295776
        ],
        "labels": [2, 2, 1, 2, 1, 1, 2, 3, 0],
        "boxes": [
            [-0.3175201416015625, 43.53631591796875, 362.50933837890625, 67.26876831054688],
            [-0.5251426696777344, 19.269771575927734, 362.5640869140625, 43.460350036621094],
            [-0.41268157958984375, 0.794677734375, 128.8265838623047, 86.2611312866211],
            [-0.4305534362792969, 0.80535888671875, 362.67877197265625, 18.99618148803711],
            [129.67820739746094, 0.8213462829589844, 252.4720458984375, 86.1773452758789],
            [251.82122802734375, 0.8133773803710938, 362.7557678222656, 86.11017608642578],
            [-0.3641777038574219, 67.27252197265625, 362.414794921875, 86.34217834472656],
            [-0.4329795837402344, 0.8099098205566406, 362.6827087402344, 18.966079711914062],
            [-0.43839263916015625, 0.771270751953125, 362.543212890625, 86.21470642089844]
        ]
    }
}


def test_FormattedTable_from_dict(doc_tiny):
    # create a CroppedTable object
    page = doc_tiny[0]
    formatted_table = TATRFormattedTable.from_dict(tiny_old_info, page)
    df = formatted_table.df()
    # get csv as string
    csv_str = df.to_csv(index=False, lineterminator='\n')
    
    assert csv_str == """Name,Celsius,Fahrenheit
Water Freezing Point,0,32
Water Boiling Point,100,212
Body Temperature,37,98.6
"""

def test_FormattedTable_to_dict(doc_tiny):
    # assert that to_dict o from_dict is identity
    page = doc_tiny[0]
    dict2table = TATRFormattedTable.from_dict(tiny_info, page)
    dict2table2dict = dict2table.to_dict()
    
    with open("test/outputs/actual/tiny_df.info", "w") as f:
        json.dump(dict2table2dict, f, indent=4)
    assert dict2table2dict == tiny_info



pdf9_t4_info = {
  "filename": "test/samples/9.pdf",
  "page_no": 8,
  "bbox": [71.3222885131836, 54.75971984863281, 529.1936645507812, 716.1232299804688],
  "confidence_score": 0.9999405145645142,
  "label": 1,
  "angle": 90,
  "config": {},
  "outliers": None,
  "fctn_results": {
    "scores": [
      0.9842957258224487,
      0.999271810054779,
      0.9934032559394836,
      0.9404571652412415,
      0.9998828172683716,
      0.9996088147163391,
      0.9748851656913757,
      0.9998244643211365,
      0.6015468239784241,
      0.9968421459197998,
      0.9994137287139893,
      0.980539083480835,
      0.5044581890106201,
      0.9998237490653992,
      0.998504638671875,
      0.9899978041648865,
      0.9961422085762024,
      0.7736825942993164,
      0.9995275735855103,
      0.9999322891235352,
      0.9957051873207092,
      0.9987722039222717,
      0.3259543776512146,
      0.5666707158088684,
      0.9997897744178772,
      0.9999086856842041,
      0.7349497675895691,
      0.9920029640197754,
      0.9998973608016968,
      0.9939077496528625,
      0.9987345337867737,
      0.8892227411270142,
      0.9992768168449402,
      0.9992066025733948,
      0.7395164966583252,
      0.5530655384063721,
      0.99224454164505,
      0.9972781538963318,
      0.5583462119102478,
      0.9999921321868896,
      0.7593361139297485
    ],
    "labels": [2,2,2,2,1,1,2,1,2,2,2,2,2,1,2,2,2,2,2,1,2,2,2,2,2,1,2,1,1,2,3,2,1,2,5,2,2,2,2,0,2],
    "boxes": [
      [-4.293132781982422, 321.1410827636719, 664.5855102539062, 333.90533447265625],
      [-3.8783950805664062, 409.8612060546875, 665.0097045898438, 431.79345703125],
      [-3.0246658325195312, 64.23762512207031, 664.3525390625, 83.87281799316406],
      [-4.081779479980469, 295.9303283691406, 664.5523681640625, 309.0666809082031],
      [433.8346862792969, -9.781600952148438, 543.6539306640625, 461.76287841796875],
      [298.5074768066406, -9.895622253417969, 359.4546813964844, 461.13568115234375],
      [-4.223793029785156, 308.65985107421875, 664.6671752929688, 321.62109375],
      [361.949462890625, -9.852771759033203, 433.7809143066406, 461.870849609375],
      [-5.017375946044922, 256.3321228027344, 666.3287353515625, 269.0086669921875],
      [-2.704151153564453, 45.010719299316406, 664.4896240234375, 63.81471252441406],
      [-2.5793685913085938, 23.878616333007812, 664.671875, 44.61714172363281],
      [-3.4918479919433594, 197.73370361328125, 664.56298828125, 227.46719360351562],
      [-3.3415870666503906, 83.7440185546875, 663.9608154296875, 103.4356689453125],
      [-3.9108238220214844, -9.526649475097656, 88.30096435546875, 463.50640869140625],
      [-3.630481719970703, 123.80007934570312, 664.3408813476562, 143.31150817871094],
      [-4.569972991943359, 333.8477783203125, 665.0905151367188, 346.7665710449219],
      [-2.9522056579589844, 142.1297149658203, 664.5438842773438, 161.68310546875],
      [-3.511322021484375, 83.90049743652344, 664.2807006835938, 103.65681457519531],
      [-3.9519882202148438, 388.1171569824219, 664.8987426757812, 410.2270812988281],
      [170.86842346191406, -10.011062622070312, 298.443115234375, 463.474365234375],
      [-3.3932266235351562, 161.29238891601562, 664.8977661132812, 179.55755615234375],
      [-3.5997352600097656, 103.7183837890625, 664.4732666015625, 123.51246643066406],
      [-4.3833160400390625, 265.34002685546875, 665.7861328125, 278.05706787109375],
      [-3.2180824279785156, 204.9288330078125, 663.9043579101562, 234.68496704101562],
      [-2.7462425231933594, -9.757110595703125, 664.7783813476562, 23.65575408935547],
      [543.0700073242188, -9.884147644042969, 610.7828369140625, 461.9019775390625],
      [-4.022747039794922, 269.82647705078125, 665.1953125, 281.98773193359375],
      [143.46678161621094, -9.552703857421875, 172.64178466796875, 462.30047607421875],
      [611.6483154296875, -9.747798919677734, 664.9022216796875, 462.0599365234375],
      [-3.5203514099121094, 431.97332763671875, 665.137939453125, 461.05523681640625],
      [-2.436199188232422, -9.790359497070312, 664.5775146484375, 23.686782836914062],
      [-3.952411651611328, 283.47076416015625, 664.5775146484375, 296.7345886230469],
      [86.84481811523438, -9.799240112304688, 143.13116455078125, 463.42755126953125],
      [-4.222988128662109, 366.6866455078125, 665.0166015625, 389.3929748535156],
      [-4.100688934326172, 27.17266845703125, 87.97344970703125, 343.62664794921875],
      [-4.024589538574219, 243.29043579101562, 664.5476684570312, 264.731689453125],
      [-3.645111083984375, 180.8434600830078, 664.7822875976562, 199.72979736328125],
      [-4.5276947021484375, 346.6362609863281, 665.1278076171875, 367.3946533203125],
      [-3.9515838623046875, 229.61300659179688, 665.32861328125, 254.5283203125],
      [-2.784954071044922, -9.479969024658203, 665.0725708007812, 462.51226806640625],
      [-3.5050582885742188, 215.72073364257812, 664.1806030273438, 245.06387329101562]
    ]
  }
}
def test_RotatedCroppedTable_from_to_dict(doc_9):
    # create a CroppedTable object
    page = doc_9[8]
    dict2table = TATRFormattedTable.from_dict(pdf9_t4_info, page)
    assert isinstance(dict2table, RotatedCroppedTable)
    assert dict2table.angle == 90
    
    dict2table2dict = dict2table.to_dict()
    assert dict2table2dict == pdf9_t4_info
    
    # test a simpler subset
    dict2simple = RotatedCroppedTable.from_dict(pdf9_t4_info, page)
    assert dict2simple.to_dict() == {
        "filename": "test/samples/9.pdf",
        "page_no": 8,
        "bbox": [
            71.3222885131836,
            54.75971984863281,
            529.1936645507812,
            716.1232299804688
        ],
        "confidence_score": 0.9999405145645142,
        "label": 1,
        "angle": 90
    }
    
    
toy_info = {
  "filename": "test/samples/9.pdf",
  "page_no": 8,
  "bbox": [71, 54.75, 529.1, 0.0],
  "confidence_score": 0.99,
  "label": 1,
  "angle": 180,
  "config": {"verbosity": 3, "force_large_table_assumption": True},
  "outliers": None,
  "fctn_results": {
    "scores": [
      0.9842957258224487,
      0.999271810054779,
      0.9934032559394836,
      0.9404571652412415,
      0.9998828172683716
    ],
    "labels": [2,2,2,2,1],
    "boxes": [
      [-4.293132781982422, 321.1410827636719, 664.5855102539062, 333.90533447265625],
      [-3.8783950805664062, 409.8612060546875, 665.0097045898438, 431.79345703125],
      [-3.0246658325195312, 64.23762512207031, 664.3525390625, 83.87281799316406],
      [-4.081779479980469, 295.9303283691406, 664.5523681640625, 309.0666809082031],
      [433.8346862792969, -9.781600952148438, 543.6539306640625, 461.76287841796875]
    ]
  }
}

def test_config_serial(doc_9):
    toy_copy = copy.deepcopy(toy_info)
    toy_copy['config']['not_actually_a_config'] = 999
    with pytest.raises(TypeError):
        table = TATRFormattedTable.from_dict(toy_copy, doc_9[8])
        
    table = TATRFormattedTable.from_dict(toy_info, doc_9[8])
    assert table.config.verbosity == 3
    assert table.config.force_large_table_assumption == True
    assert table.angle == 180
    
    # test to_dict
    table_dict = table.to_dict()
    assert table_dict == toy_info

# def test_config():
#     from gmft.formatters.tatr import TATRFormatConfig
#     from dataclasses import fields
    
#     print(fields(TATRFormatConfig))
    # config = TATRFormatConfig(force_large_table_assumption=True, verbosity=3)
    # assert config.verbosity == 3
    # assert config.force_large_table_assumption == True
/**
 * Region curated day-course list for travel-courses hub.
 * Same chrome for every region: intro → course chips → detail (map + timetable).
 * Data: window.CURATED_COURSES_BY_REGION[regionId]
 * Seoul copy: travelCourses.seoulCurated.* — other regions: travelCourses.curated.*
 */
(function () {
  var ROOT_SEL = "[data-region-curated], [data-seoul-curated]";
  var liveMaps = [];
  var REGION_I18N = {
    seoul: "travelCourses.regionSeoul",
    incheon: "travelCourses.regionIncheon",
    gyeonggi: "travelCourses.regionGyeonggi",
    gangwon: "travelCourses.regionGangwon",
    chungcheong: "travelCourses.regionChungcheong",
    jeolla: "travelCourses.regionJeolla",
    gyeongsang: "travelCourses.regionGyeongsang",
    busan: "travelCourses.regionBusan",
    jeju: "travelCourses.regionJeju",
  };

  var SLUG_COORDS = {
    "ssamziegil": [37.5741, 126.9847],
    "ikseon-dong": [37.5744, 126.9898],
    "n-seoul-tower": [37.5512, 126.9882],
    "namsan-park": [37.5545, 126.9838],
    "yongsan-station": [37.5299, 126.9648],
    "apgujeong-rodeo": [37.5275, 127.0406],
    "seoullo-7017": [37.5567, 126.9738],
    "euljiro": [37.566, 126.991],
    "seongsu-cafe": [37.5445, 127.0557],
    "seongsu-popup": [37.5448, 127.0518],
    "seongsu-dong": [37.5445, 127.0557],
    "ttukseom-hangang": [37.5305, 127.0668],
    "konkuk-food-street": [37.5407, 127.0692],
    "konkuk-university": [37.5404, 127.0796],
    "yeonnam-cafe": [37.5623, 126.9254],
    "yeonnam-dong": [37.5623, 126.9254],
    "hongdae-street": [37.5563, 126.9236],
    "hongdae-shops": [37.5555, 126.9218],
    "mangwon-hangang": [37.5556, 126.893],
    "byeolmadang-library": [37.5116, 127.0595],
    "garosu-gil": [37.521, 127.0229],
    "boteunsa": [37.5145, 127.0574],
    "seokchon-lake": [37.511, 127.103],
    "lotte-world": [37.5111, 127.098],
    "naksan-park": [37.5808, 127.0076],
    "ihwa-mural-village": [37.579, 127.0078],
    "daehangno": [37.5826, 127.002],
    "marronnier-park": [37.5804, 127.0027],
    "ddp": [37.5668, 127.0094],
    "the-hyundai-seoul": [37.5258, 126.9286],
    "yeouido": [37.5219, 126.9245],
    "seochon": [37.5788, 126.9688],
    "seochon-cafe": [37.5794, 126.9696],
    "gwathwamun": [37.5716, 126.9769],
    "hannam-dong": [37.5345, 127.0028],
    "itaewon-street": [37.5345, 126.9946],
    "gyeongnidan-gil": [37.5412, 126.9868],
    "haebangchon": [37.542, 126.9865],
    "yongridan-gil": [37.53, 126.9678],
    "bosingak": [37.57, 126.9833],
    "songridan-gil": [37.5055, 127.1065],
    "jamsil-skyline": [37.5126, 127.1025],
    "sebit-seom": [37.5125, 126.996],
    "hangang-yeouido": [37.5285, 126.934],
    "hangang-yeouido-cafe": [37.5285, 126.934],
    "hangang-banpo": [37.5105, 126.996],
    "hangang-banpo-fountain": [37.5142, 126.9968],
    "national-museum-korea": [37.5239, 126.9803],
    "cheongdam-fashion": [37.5245, 127.047],
    "cheonggyecheon": [37.5692, 126.9975],
    "cheonggyecheon-plaza": [37.5695, 126.9788],
    "gwangjang-market": [37.57, 126.9996],
    "insadong": [37.5717, 126.9858],
    "ichon-hangang": [37.5178, 126.9756],
    "dosan-park": [37.5226, 127.0356],
    "bukjeong-village": [37.5926, 127.0038],
    "seongbuk-dong": [37.5922, 126.9984],
    "hansung-univ": [37.5884, 127.0062],
    "haenggungdong": [37.281, 127.0159],
    "hwaseong-haenggung": [37.2825, 127.0145],
    "haengnidangil": [37.2838, 127.0172],
    "banghwasuryujeong": [37.2878, 127.0186],
    "paldalmun": [37.2776, 127.0169],
    "janganmun": [37.2889, 127.0098],
    "suwon-night": [37.2848, 127.0092],
    "hangukminsokchon": [37.2585, 127.1175],
    "bojeong-cafe": [37.3218, 127.1112],
    "jukjeon": [37.3246, 127.1074],
    "nami-island": [37.7916, 127.5254],
    "nami-lunch": [37.7902, 127.5282],
    "petit-france": [37.7147, 127.4903],
    "garden-of-morning-calm": [37.7439, 127.3525],
    "dmz": [37.9073, 126.7036],
    "imjingak": [37.8892, 126.7403],
    "imjingak-lunch": [37.8878, 126.7382],
    "heyri": [37.7786, 126.6985],
    "heyri-cafe": [37.7765, 126.6958],
    "provence-village": [37.7718, 126.6905],
    "dumulmeori": [37.5408, 127.3096],
    "semiwon": [37.5413, 127.3215],
    "yangpyeong": [37.4912, 127.4876],
    "yangsu-lunch": [37.5422, 127.315],
    "yangpyeong-cafe": [37.5386, 127.3072],
    "namhangang": [37.5374, 127.3048],
    "gwangmyeong-cave": [37.4255, 126.8655],
    "gwangmyeong-lunch": [37.427, 126.8676],
    "gwangmyeong-market": [37.4762, 126.8668],
    "gwangmyeong-cafe": [37.4782, 126.8655],
    "cheolsan": [37.4765, 126.8685],
    "dasan-historic": [37.5548, 127.2408],
    "silhakbakmulgwan": [37.5542, 127.2392],
    "bukhangang": [37.5804, 127.2406],
    "mului-garden": [37.5806, 127.2289],
    "namyangju": [37.636, 127.2165],
    "pocheon-art-valley": [37.9192, 127.2361],
    "pocheon-art-lunch": [37.9175, 127.2338],
    "sanjeong-lake": [37.9292, 127.3235],
    "sanjeong-cafe": [37.9278, 127.3258],
    "pocheon": [37.8949, 127.2003],
    "herb-island": [37.9664, 127.1336],
    "icheon-yespark": [37.2878, 127.4122],
    "icheon-cerapia": [37.2805, 127.4438],
    "icheon": [37.2723, 127.435],
    "yeoju-namhangang": [37.2988, 127.6572],
    "sinreuksa": [37.2975, 127.6553],
    "sinreuksa-lunch": [37.2964, 127.6536],
    "sejong-tomb": [37.3098, 127.6058],
    "yeoju-outlet": [37.2415, 127.6135],
    "gaetgol": [37.3906, 126.7831],
    "oido": [37.3456, 126.6878],
    "oido-lighthouse": [37.3415, 126.6978],
    "daebudo": [37.277, 126.58],
    "bada-hyanggi": [37.2206, 126.5786],
    "tando-port": [37.1928, 126.6465],
    "namhansanseong": [37.4785, 127.1825],
    "namhansanseong-nammun": [37.4748, 127.1815],
    "namhansanseong-wall": [37.4816, 127.1856],
    "namhansanseong-maeul": [37.4778, 127.1812],
    "namhansanseong-seomun": [37.4792, 127.1755],
    "namhansanseong-cafe": [37.477, 127.18],
    "everland": [37.294, 127.2023],
    "everland-lunch": [37.2946, 127.201],
    "everland-safari": [37.2968, 127.2048],
    "everland-garden": [37.2918, 127.1995],
    "everland-dinner": [37.2948, 127.2038],
    "everland-night": [37.2934, 127.2056],
    "hangukminsokchon-exit": [37.2568, 127.1158],
    "pangyo": [37.3945, 127.1112],
    "incheon-chinatown": [37.4746, 126.6194],
    "incheon-chinatown-lunch": [37.4737, 126.6182],
    "jayu-park": [37.4751, 126.6224],
    "gaehangjang": [37.4735, 126.6215],
    "sinpo-international-market": [37.4713, 126.6271],
    "wolmido": [37.473, 126.6028],
    "wolmido-dinner": [37.4716, 126.6005],
    "songdo": [37.3928, 126.6388],
    "songdo-lunch": [37.3949, 126.6436],
    "tribowl": [37.3939, 126.6336],
    "hyundai-premium-outlet-songdo": [37.3815, 126.6595],
    "songdo-sunset": [37.391, 126.6412],
    "songdo-dinner": [37.3956, 126.6452],
    "songdo-night": [37.3896, 126.644],
    "masian-beach": [37.4194, 126.4212],
    "masian-lunch": [37.4186, 126.4194],
    "masian-cafe": [37.4174, 126.4176],
    "masian-dinner": [37.4165, 126.422],
    "eulwangni-beach": [37.4475, 126.3725],
    "eulwangni-walk": [37.4488, 126.3708],
    "eulwangni-sunset": [37.4496, 126.3688],
    "eulwangni-dinner": [37.4462, 126.3748],
    "paradise-city": [37.437, 126.4567],
    "paradise-city-lunch": [37.4362, 126.4586],
    "paradise-city-arts": [37.438, 126.4548],
    "dongmak-beach": [37.5928, 126.4672],
    "dongmak-cafe": [37.595, 126.4738],
    "ganghwa-coast": [37.6306, 126.5319],
    "ganghwa-peace": [37.8267, 126.4332],
    "ganghwa-peace-cafe": [37.8248, 126.4315],
    "jeondeungsa": [37.6325, 126.4855],
    "jeondeungsa-onsu": [37.6349, 126.4886],
    "gathwa-goindol": [37.7255, 126.4455],
    "gwongeumseong": [38.1632, 128.4924],
    "seoraksan-sogongwon": [38.1731, 128.4891],
    "sokcho-tourist-fish-market": [38.2045, 128.5918],
    "sokcho-beach": [38.1908, 128.6035],
    "oeongchi": [38.1845, 128.6162],
    "daepohang": [38.1756, 128.6084],
    "gyeongpodae": [37.7952, 128.8964],
    "gyeongpo-beach": [37.8058, 128.9088],
    "gangneung-jungang-market": [37.7542, 128.8971],
    "anmok-coffee": [37.7714, 128.9478],
    "gangmun-beach": [37.7948, 128.9186],
    "gangneung-dinner": [37.7714, 128.9478],
    "chuncheon-dakgalbi": [37.8815, 127.7298],
    "uiamho": [37.8582, 127.6934],
    "chuncheon-downtown": [37.8815, 127.7298],
    "daegwallyeong-sheep": [37.6868, 128.7526],
    "pyeongchang-lunch": [37.6708, 128.7096],
    "daegwallyeong": [37.6865, 128.7182],
    "woljeongsa": [37.7314, 128.5926],
    "woljeongsa-fir": [37.7332, 128.5941],
    "yangyang-lunch": [38.0752, 128.6194],
    "naksan-beach": [38.1224, 128.6282],
    "hajodae": [38.0386, 128.7192],
    "yangyang-dinner": [38.0752, 128.6194],
    "chuam-candle": [37.4782, 129.1594],
    "chuam-beach": [37.4764, 129.1618],
    "donghae-lunch": [37.5248, 129.1142],
    "dojjaebigol": [37.4872, 129.1446],
    "mukho-nongol": [37.5548, 129.1168],
    "donghae-dinner": [37.5248, 129.1142],
    "hantan-columnar": [38.2012, 127.2864],
    "cheorwon-lunch": [38.1462, 127.3134],
    "goseokjeong": [38.1852, 127.3052],
    "cheorwon-dmz": [38.2924, 127.2376],
    "gongsanseong": [36.4632, 127.1264],
    "gongju-sanseong-market": [36.4578, 127.1212],
    "muryeong-tombs": [36.4524, 127.1142],
    "gongju-museum": [36.4552, 127.1114],
    "jemincheon": [36.4512, 127.1242],
    "gongju-dinner": [36.4512, 127.1242],
    "busosanseong": [36.2794, 126.9122],
    "buyeo-lunch": [36.2752, 126.9094],
    "gungnamji": [36.2692, 126.9124],
    "buyeo-museum": [36.2762, 126.9192],
    "jeongnimsaji": [36.2754, 126.9132],
    "buyeo-downtown": [36.2752, 126.9094],
    "dodamsambong": [36.9988, 128.3422],
    "mancheonha": [36.9872, 128.3654],
    "danyang-lunch": [36.9848, 128.3652],
    "danyang-jando": [36.9862, 128.3702],
    "danyang-paragliding": [36.9734, 128.3652],
    "danyang-market": [36.9848, 128.3662],
    "daecheon-beach": [36.3052, 126.5142],
    "daecheon-lunch": [36.3072, 126.5124],
    "daecheon-skybike": [36.3192, 126.5112],
    "daecheon-cafe": [36.3102, 126.5124],
    "daecheon-walk": [36.3115, 126.5128],
    "daecheon-sunset": [36.3012, 126.5158],
    "daecheon-dinner": [36.3072, 126.5124],
    "anmyeondo": [36.5088, 126.3302],
    "taean-lunch": [36.7452, 126.2982],
    "kkoji-beach": [36.5042, 126.3332],
    "taean-cafe": [36.506, 126.3355],
    "kkoji-sunset": [36.5006, 126.332],
    "taean-dinner": [36.5042, 126.3332],
    "national-science-museum": [36.3758, 127.3756],
    "daejeon-lunch": [36.3512, 127.3848],
    "hanbit-tower": [36.3764, 127.3862],
    "sungsimdang": [36.3278, 127.4272],
    "daejeon-downtown": [36.3278, 127.4252],
    "daejeon-dinner": [36.3278, 127.4252],
    "gyeonggijeon": [35.8154, 127.1498],
    "jeonju-bibimbap": [35.8152, 127.1498],
    "jeondong-cathedral": [35.8134, 127.1492],
    "jeonju-hanok-cafe": [35.8152, 127.1522],
    "jeonju-nambu-market": [35.8122, 127.1476],
    "jeonju-dinner": [35.8122, 127.1476],
    "yeosu-lunch": [34.7402, 127.7372],
    "yeosu-cable": [34.7392, 127.7456],
    "dolsan-park": [34.7312, 127.7482],
    "isunsin-square": [34.7402, 127.7368],
    "nangman-pocha": [34.7386, 127.7362],
    "yeosu-night": [34.7386, 127.7362],
    "suncheon-garden": [34.9286, 127.5094],
    "suncheon-lunch": [34.9504, 127.4872],
    "yongsan-observatory": [34.8602, 127.5142],
    "suncheon-sunset": [34.8602, 127.5142],
    "suncheon-dinner": [34.9504, 127.4872],
    "juknokwon": [35.3296, 126.9864],
    "gwanbangjerim": [35.3224, 126.9852],
    "damyang-lunch": [35.3212, 126.9882],
    "metasequoia-damyang": [35.3228, 126.9968],
    "damyang-cafe": [35.3234, 126.9982],
    "metaprovence": [35.3218, 127.0012],
    "boseong-lunch": [34.7632, 127.0802],
    "boseong-tea-cafe": [34.7142, 127.0812],
    "yulpo-beach": [34.6712, 127.0836],
    "yulpo-coast": [34.6735, 127.086],
    "boseong-dinner": [34.6712, 127.0836],
    "mokpo-modern": [34.7855, 126.3855],
    "mokpo-lunch": [34.7932, 126.3882],
    "mokpo-cable": [34.7912, 126.3752],
    "yudalsan": [34.7916, 126.3738],
    "gatbawi-mokpo": [34.7822, 126.3756],
    "mokpo-dinner": [34.7932, 126.3882],
    "daereungwon": [35.8378, 129.2118],
    "cheomseongdae": [35.8346, 129.219],
    "gyochon-woljeonggyo": [35.8296, 129.2186],
    "buyongdae": [36.5408, 128.5162],
    "andong-lunch": [36.5388, 128.5182],
    "hahoe-mask": [36.5394, 128.5186],
    "byeongsanseowon": [36.4624, 128.4906],
    "woryeonggyo": [36.5688, 128.7752],
    "andong-dinner": [36.5688, 128.7752],
    "tongyeong-cable": [34.8255, 128.4138],
    "mireuksan": [34.824, 128.4088],
    "tongyeong-jungang-market": [34.8426, 128.4248],
    "dongpirang": [34.8452, 128.4276],
    "gangguan": [34.8428, 128.4236],
    "yi-sun-sin-park": [34.8276, 128.4372],
    "tongyeong-dinner": [34.8426, 128.4248],
    "geoje-pier": [34.7512, 128.6632],
    "haegeumgang": [34.7348, 128.6824],
    "oeodo-botania": [34.7108, 128.7126],
    "geoje-lunch": [34.8045, 128.6908],
    "baramui-eondeok": [34.7448, 128.6638],
    "sinseondae": [34.7412, 128.6648],
    "geoje-dinner": [34.8045, 128.6908],
    "pohang-jukdo-market": [36.0348, 129.3672],
    "pohang-lunch": [36.0348, 129.3672],
    "yeongildae-beach": [36.0518, 129.3786],
    "spacewalk": [36.0658, 129.3908],
    "pohang-cafe": [36.0518, 129.3786],
    "yeongildae-night": [36.0518, 129.3786],
    "homigot": [36.0768, 129.5682],
    "guryongpo-houses": [36.1086, 129.5554],
    "guryongpo-lunch": [36.1086, 129.5554],
    "guryongpo-port": [36.1054, 129.5558],
    "guryongpo-cafe": [36.1052, 129.5786],
    "pohang-return": [36.0322, 129.3652],
    "seomun-market": [35.8686, 128.5804],
    "daegu-lunch": [35.8686, 128.5804],
    "daegu-modern": [35.8698, 128.5908],
    "dongseong-ro": [35.8708, 128.5956],
    "apsan": [35.8252, 128.5772],
    "apsan-night": [35.8252, 128.5772],
    "taehwa-garden": [35.5496, 129.2964],
    "ulsan-lunch": [35.5386, 129.3114],
    "ulsan-ilsan-beach": [35.4978, 129.4308],
    "ulsan-coast": [35.4945, 129.4345],
    "ulsan-dinner": [35.4978, 129.4308],
    "haeinsa-lunch": [35.8015, 128.0975],
    "tripitaka": [35.8015, 128.0975],
    "hapcheon-cafe": [35.8015, 128.0975],
    "dongbaekseom": [35.1536, 129.1528],
    "haeundae-lunch": [35.1587, 129.1604],
    "blueline-cheongsapo": [35.1608, 129.1914],
    "daritdol": [35.1602, 129.1918],
    "gwangalli": [35.1532, 129.1186],
    "gwangalli-dinner": [35.1532, 129.1186],
    "jagalchi": [35.0966, 129.0306],
    "gukje-market": [35.0986, 129.0286],
    "yongdusan": [35.1008, 129.0324],
    "nampo-dinner": [35.0969, 129.0306],
    "busan-songdo": [35.0758, 129.0172],
    "songdo-cable": [35.0758, 129.0172],
    "songdo-busan-lunch": [35.0758, 129.0172],
    "amnam-park": [35.0596, 129.0178],
    "huinnyeoul": [35.0786, 129.0448],
    "yeongdo-cafe": [35.0786, 129.0448],
    "yeongdo-dinner": [35.0786, 129.0448],
    "gijang-coast": [35.1884, 129.2233],
    "gijang-lunch": [35.2448, 129.2186],
    "ananti-osiria": [35.1968, 129.2286],
    "gijang-cafe": [35.1968, 129.2286],
    "gijang-sunset": [35.1884, 129.2233],
    "gijang-dinner": [35.2448, 129.2186],
    "yeongdo-lunch": [35.0504, 129.0883],
    "jeolyeong-trail": [35.0762, 129.0456],
    "busan-port-night": [35.0962, 129.0368],
    "seomyeon-lunch": [35.1576, 129.0595],
    "jeonpo-cafe": [35.1562, 129.0638],
    "jeonpo-shops": [35.1562, 129.0638],
    "seomyeon-shopping": [35.1576, 129.0595],
    "seomyeon-dinner": [35.1576, 129.0595],
    "seomyeon-night": [35.1576, 129.0595],
    "seongsan-lunch": [33.4622, 126.9328],
    "aquaplanet-jeju": [33.4336, 126.9278],
    "gwangchigi": [33.4524, 126.9242],
    "seongsan-dinner": [33.4622, 126.9328],
    "seongsan-port": [33.4724, 126.9278],
    "udo-coast": [33.5002, 126.9505],
    "udo-lunch": [33.5064, 126.9532],
    "geommeolle": [33.4972, 126.9678],
    "udo-cafe": [33.5064, 126.9532],
    "seongsan-return": [33.4724, 126.9278],
    "hyeopjae-beach": [33.3942, 126.2396],
    "geumneung-beach": [33.3896, 126.2362],
    "hallim-lunch": [33.4142, 126.2672],
    "osulloc": [33.3056, 126.2896],
    "west-jeju-cafe": [33.3056, 126.2896],
    "west-jeju-sunset": [33.3942, 126.2396],
    "aewol-coast": [33.4658, 126.3186],
    "handam": [33.4608, 126.3108],
    "aewol-lunch": [33.4658, 126.3186],
    "aewol-cafe": [33.4624, 126.3202],
    "gwakji-beach": [33.4506, 126.3052],
    "aewol-sunset": [33.4506, 126.3052],
    "aewol-dinner": [33.4658, 126.3186],
    "jeongbang-falls": [33.2448, 126.5718],
    "seogwipo-downtown": [33.2478, 126.5622],
    "olle-market": [33.2486, 126.5636],
    "cheonjiyeon": [33.2447, 126.5594],
    "saeyeongyo": [33.2408, 126.5592],
    "seogwipo-coast": [33.2408, 126.5592],
    "seogwipo-dinner": [33.2478, 126.5622],
    "jungmun-beach": [33.2452, 126.4122],
    "jungmun-lunch": [33.2452, 126.4122],
    "yeomiji": [33.2524, 126.4136],
    "jungmun-resort": [33.2472, 126.4128],
    "jungmun-cafe": [33.2472, 126.4128],
    "jungmun-dinner": [33.2472, 126.4128],
    "hallasan-start": [33.3847, 126.6203],
    "hallasan-summit": [33.3617, 126.5292],
    "hallasan-descent": [33.3594, 126.5456],
    "hallasan-dinner": [33.4892, 126.4982],
    "yongduam": [33.5162, 126.5122],
    "yongyeon": [33.5148, 126.5256],
    "jejusi-lunch": [33.5126, 126.5232],
    "jejumok-gwana": [33.5124, 126.5218],
    "jeju-dongmun-market": [33.5118, 126.5264],
    "tapdong": [33.5172, 126.5268],
    "dongmun-dinner": [33.5118, 126.5264],
    "woljeong-beach": [33.5564, 126.7958],
    "woljeong-lunch": [33.5564, 126.7958],
    "yongnuni-oreum": [33.4596, 126.8312],
    "sehwa-beach": [33.5256, 126.8602],
    "east-jeju-cafe": [33.5256, 126.8602],
    "sanbangsan": [33.2416, 126.3136],
    "sagye-lunch": [33.2378, 126.2992],
    "songaksan": [33.2056, 126.2908],
    "sagye-coast": [33.2318, 126.2996],
    "southwest-sunset": [33.2056, 126.2908],
    "hwangnidan-lunch": [35.8362, 129.2115],
    "gayasan": [35.8025, 128.1225],
    "seongsan-cafe": [33.4612, 126.9345],
    "cheongsapo": [35.1588, 129.1915],
    "yeongdo-cafe-2": [35.0772, 129.0488],
    "omokdae": [35.8155, 127.1555],
    "odongdo": [34.74504, 127.76709],
    "udo": [33.50726, 126.955],
    "bijarim": [33.49318, 126.81034],
    "jusangjeolli": [33.2375, 126.4245],
    "taejongdae": [35.05039, 129.08829],
    "haedong": [35.1884, 129.2233],
    "seopjikoji": [33.4245, 126.9305],
    "samaksan": [37.83972, 127.66037],
    "boseong": [34.714, 127.081],
    "hahoe": [36.5391, 128.5178],
    "bulguksa": [35.79, 129.332],
    "donggung": [35.8347, 129.2268],
    "jeonju": [35.815, 127.153],
    "seongsan": [33.4581, 126.9425],
    "jungmun": [33.2427, 126.4127],
    "gamcheon": [35.0975, 129.0104],
    "haeundae": [35.1587, 129.1604],
    "nampo": [35.0969, 129.0306],
    "seomyeon": [35.1576, 129.0595],
    "hallasan": [33.3847, 126.6203],
    "seoraksan": [38.1195, 128.4654],
    "suncheon-bay": [34.8852, 127.5103],
    "naksansa": [38.1255, 128.6255],
    "haeinsa": [35.8015, 128.0975],
    "biff-square": [35.0989, 129.0291],
  };

  var SLUG_ALIAS = {
    "hongdae-street": "hongdae",
    "hongdae-shops": "hongdae",
    "hangang-banpo-fountain": "hangang-banpo",
    "itaewon-street": "itaewon",
    "ddp": "dongdaemun",
    "byeolmadang-library": "coex",
    "n-seoul-tower": "namsan",
    "cheongdam-fashion": "cheongdam",
    "jamsil-skyline": "lotte-tower",
    "seongsu-cafe": "seongsu-dong",
    "seongsu-popup": "seongsu-dong",
    "yeonnam-cafe": "hongdae",
    "hwaseong-haenggung": "hwaseothaetgut",
    "gwangmyeong-cave": "gwatmyeotdotgul",
    "namhansanseong": "nalhansanseot",
    "sejong-tomb": "sejotdaewatreut",
    "jeondeungsa": "gathwa-jeondeutsa",
    "gaehangjang": "incheon-gaehatjat-munhwajigu",
    "gongsanseong": "gotsanseot",
    "busosanseong": "busosanseot",
    "buyeo-museum": "gukrimbuyeobakmulgwan",
    "mokpo-modern": "mokpo-geundaeyeoksamunhwagotgan",
    "gyeongpodae": "gyeotpodae",
    "daereungwon": "daereutwon",
    "jeondong-cathedral": "jeonju",
    "gyeonggijeon": "jeonju",
  };

  function t(key, fallback) {
    try {
      if (window.GuideI18n && typeof window.GuideI18n.t === "function") {
        return window.GuideI18n.t(key, fallback || key);
      }
    } catch (e) {
      /* ignore */
    }
    return fallback || key;
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escapeAttr(s) {
    return escapeHtml(s).replace(/'/g, "&#39;");
  }

  function regionId(root) {
    if (!root) return "seoul";
    return (
      root.getAttribute("data-region-curated") ||
      (root.hasAttribute("data-seoul-curated") ? "seoul" : "seoul")
    );
  }

  function regionLabel(id) {
    return t(REGION_I18N[id] || "travelCourses.regionSeoul", id);
  }

  function fillRegion(str, name) {
    return String(str || "").replace(/\{region\}/g, name);
  }

  function coursesFor(region) {
    var byRegion = window.CURATED_COURSES_BY_REGION || {};
    if (Array.isArray(byRegion[region])) return byRegion[region];
    if (region === "seoul" && Array.isArray(window.SEOUL_CURATED_COURSES)) {
      return window.SEOUL_CURATED_COURSES;
    }
    return [];
  }

  function courseCopyBase(region, id) {
    if (region === "seoul") {
      return "travelCourses.seoulCurated.courses." + id;
    }
    return "travelCourses.curated." + region + ".courses." + id;
  }

  function courseCopy(region, id) {
    var base = courseCopyBase(region, id);
    var notice = t(base + ".notice", "");
    if (notice === base + ".notice") notice = "";
    return {
      title: t(base + ".title", id),
      summary: t(base + ".summary", ""),
      route: t(base + ".route", ""),
      tips: t(base + ".tips", ""),
      notice: notice,
    };
  }

  function stopCopy(region, id, index) {
    var base = courseCopyBase(region, id) + ".stops." + index;
    return {
      name: t(base + ".name", ""),
      desc: t(base + ".desc", ""),
    };
  }

  function chromeCopy(region) {
    var name = regionLabel(region);
    if (region === "seoul") {
      return {
        pickLabel: t("travelCourses.seoulCurated.pickLabel", "서울 추천 코스"),
        intro: t(
          "travelCourses.seoulCurated.intro",
          "서울을 하루 만에 알차게 도는 대표 코스입니다."
        ),
        guideEyebrow: t("travelCourses.seoulCurated.guideEyebrow", "서울 코스 안내"),
      };
    }
    var pickKey = "travelCourses.curated." + region + ".pickLabel";
    var introKey = "travelCourses.curated." + region + ".intro";
    var eyeKey = "travelCourses.curated." + region + ".guideEyebrow";
    var pick = t(pickKey, "");
    var intro = t(introKey, "");
    var eye = t(eyeKey, "");
    if (!pick || pick === pickKey) {
      pick = t("travelCourses.curated.pickLabel", "{region} 추천 코스");
    }
    if (!intro || intro === introKey) {
      intro = t(
        "travelCourses.curated.intro",
        "이 지역의 대표 코스 설명서입니다. 코스가 추가되면 타이틀을 고르고 소개·동선·시간표를 확인할 수 있습니다."
      );
    }
    if (!eye || eye === eyeKey) {
      eye = t("travelCourses.curated.guideEyebrow", "{region} 코스 안내");
    }
    return {
      pickLabel: fillRegion(pick, name),
      intro: fillRegion(intro, name),
      guideEyebrow: fillRegion(eye, name),
    };
  }

  function imgSrc(path) {
    if (!path) return "../../Images/travel-courses/_fallback.jpg";
    var src = path;
    if (!(path.indexOf("../../") === 0 || path.indexOf("../") === 0)) {
      src = "../../" + String(path).replace(/^\.\//, "");
    }
    var v = (window.SITE_ASSET_VERSION || "").toString();
    if (v && src.indexOf("?") === -1) src += "?v=" + encodeURIComponent(v);
    return src;
  }

  function imageSlug(path) {
    return String(path || "")
      .split("/")
      .pop()
      .replace(/\.(jpg|jpeg|png|webp)$/i, "")
      .replace(/^\d{2}-/, "");
  }

  function placeIndex() {
    var index = {};
    (window.PLACES_COORDS || []).forEach(function (p) {
      index[p.slug] = p;
    });
    return index;
  }

  function lookupCoord(slug, index) {
    if (!slug) return null;
    if (SLUG_COORDS[slug]) {
      return { lat: SLUG_COORDS[slug][0], lng: SLUG_COORDS[slug][1] };
    }
    if (index[slug]) return index[slug];
    var alias = SLUG_ALIAS[slug];
    if (alias && SLUG_COORDS[alias]) {
      return { lat: SLUG_COORDS[alias][0], lng: SLUG_COORDS[alias][1] };
    }
    if (alias && index[alias]) return index[alias];
    return null;
  }

  function firstClock(s) {
    var m = String(s || "").match(/\d{1,2}:\d{2}/);
    return m ? m[0] : "";
  }

  function lastClock(s) {
    var m = String(s || "").match(/\d{1,2}:\d{2}/g);
    return m && m.length ? m[m.length - 1] : "";
  }

  function diffHours(start, end) {
    start = firstClock(start);
    end = lastClock(end);
    if (!start || !end || start.indexOf(":") === -1 || end.indexOf(":") === -1) {
      return "";
    }
    var a = start.split(":").map(Number);
    var b = end.split(":").map(Number);
    var mins = b[0] * 60 + b[1] - (a[0] * 60 + a[1]);
    if (mins <= 0) return "";
    var hours = Math.round((mins / 60) * 10) / 10;
    return t("travelCourses.seoulCurated.meta.hours", "{hours}h").replace(
      "{hours}",
      String(hours)
    );
  }

  function courseMeta(course) {
    var stops = (course && course.stops) || [];
    var first = stops[0] && stops[0].time;
    var last = stops[stops.length - 1] && stops[stops.length - 1].time;
    return {
      totalTime: diffHours(first, last) || "-",
      stopCount: String(stops.length || 0),
      firstTime: first || "-",
      lastTime: last || "-",
    };
  }

  function icon(name) {
    if (name === "time") {
      return '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="7"></circle><path d="M10 6.5v4l2.8 1.7"></path></svg>';
    }
    if (name === "stops") {
      return '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4.5 14.5c0-2.2 1.8-4 4-4h3c2.2 0 4 1.8 4 4"></path><circle cx="10" cy="6.8" r="2.4"></circle></svg>';
    }
    if (name === "start") {
      return '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5.5 4.8v10.4L15 10z"></path></svg>';
    }
    return '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 10.6l3.2 3.2L15 6.8"></path></svg>';
  }

  function splitRoute(route) {
    return String(route || "")
      .split(/\s*→\s*|\s*->\s*|\s*➜\s*/)
      .map(function (part) {
        return part.trim();
      })
      .filter(Boolean);
  }

  function renderAside(copy, routeLabel, tipsLabel) {
    if (!copy.route && !copy.tips) return "";
    var routeHtml = "";
    if (copy.route) {
      var parts = splitRoute(copy.route);
      var hop =
        '<li class="course-guide-route__hop" aria-hidden="true">' +
        '<svg viewBox="0 0 20 20"><path d="M7 4.8l6 5.2-6 5.2"></path></svg>' +
        "</li>";
      var flow = parts
        .map(function (name, idx) {
          var extra = "";
          if (idx === 0) extra = " is-start";
          if (idx === parts.length - 1) extra += " is-end";
          return (
            '<li class="course-guide-route__stop' +
            extra +
            '">' +
            '<span class="course-guide-route__num">' +
            (idx + 1) +
            "</span>" +
            '<span class="course-guide-route__name">' +
            escapeHtml(name) +
            "</span></li>" +
            (idx < parts.length - 1 ? hop : "")
          );
        })
        .join("");
      routeHtml =
        '<div class="course-guide-route">' +
        '<p class="course-guide-route__kicker">' +
        '<span class="course-guide-route__icon" aria-hidden="true">' +
        '<svg viewBox="0 0 20 20"><circle cx="4.4" cy="14.8" r="1.7"></circle><circle cx="10" cy="5.2" r="1.7"></circle><circle cx="15.6" cy="12.6" r="1.7"></circle><path d="M5.7 13.4C7.1 11.2 8.4 7.8 10 6.8M11.5 6.6C12.8 8.2 13.9 10.4 14.6 11.2"></path></svg>' +
        "</span>" +
        escapeHtml(routeLabel) +
        "</p>" +
        '<ol class="course-guide-route__flow">' +
        (flow ||
          '<li class="course-guide-route__stop"><span class="course-guide-route__name">' +
            escapeHtml(copy.route) +
            "</span></li>") +
        "</ol></div>";
    }
    var tipsHtml = "";
    if (copy.tips) {
      tipsHtml =
        '<div class="course-guide-tips">' +
        '<span class="course-guide-tips__icon" aria-hidden="true">' +
        '<svg viewBox="0 0 20 20"><path d="M10 3.2a5 5 0 0 0-2.8 9.1c.5.4.8 1 .8 1.6v.4h4v-.4c0-.6.3-1.2.8-1.6A5 5 0 0 0 10 3.2z"></path><path d="M8.2 15.8h3.6M8.6 17.4h2.8"></path></svg>' +
        "</span>" +
        '<div class="course-guide-tips__body">' +
        '<p class="course-guide-tips__kicker">' +
        escapeHtml(tipsLabel) +
        "</p>" +
        '<p class="course-guide-tips__text">' +
        escapeHtml(copy.tips) +
        "</p></div></div>";
    }
    return (
      '<div class="course-guide-aside">' + routeHtml + tipsHtml + "</div>"
    );
  }

  function mobilityKind(course) {
    return (course && course.mobility) || "";
  }

  function mobilityLabel(kind, shortLabel) {
    if (!kind) return "";
    var key = shortLabel
      ? "travelCourses.curated.mobility." + kind + "Short"
      : "travelCourses.curated.mobility." + kind;
    var fallbacks = {
      transit: "대중교통 추천",
      car: "자동차 추천",
      mix: "대중교통·차량",
    };
    var shortFallbacks = {
      transit: "대중교통",
      car: "차량",
      mix: "혼합",
    };
    return t(key, shortLabel ? shortFallbacks[kind] : fallbacks[kind] || kind);
  }

  function mobilityBadgeHtml(kind, shortLabel) {
    if (!kind) return "";
    return (
      '<span class="course-guide-mob is-' +
      escapeAttr(kind) +
      '">' +
      escapeHtml(mobilityLabel(kind, shortLabel)) +
      "</span>"
    );
  }

  function noticeHtml(copy) {
    if (!copy || !copy.notice) return "";
    var label = t("travelCourses.curated.noticeLabel", "안내");
    return (
      '<div class="course-guide-notice">' +
      '<span class="course-guide-notice__icon" aria-hidden="true">' +
      '<svg viewBox="0 0 20 20"><circle cx="10" cy="10" r="7"></circle><path d="M10 9v4.2M10 6.4h.01"></path></svg>' +
      "</span>" +
      '<div class="course-guide-notice__body">' +
      '<p class="course-guide-notice__kicker">' +
      escapeHtml(label) +
      "</p>" +
      '<p class="course-guide-notice__text">' +
      escapeHtml(copy.notice) +
      "</p></div></div>"
    );
  }

  function renderMetaCards(course) {
    var meta = courseMeta(course);
    var labels = {
      total: t("travelCourses.seoulCurated.meta.totalTime", "총 소요"),
      stops: t("travelCourses.seoulCurated.meta.stops", "방문 포인트"),
      start: t("travelCourses.seoulCurated.meta.start", "시작 시간"),
      finish: t("travelCourses.seoulCurated.meta.finish", "마무리"),
    };
    return (
      '<div class="course-guide-meta">' +
      '<div class="course-guide-meta__item"><span class="course-guide-meta__icon">' +
      icon("time") +
      '</span><div class="course-guide-meta__text"><span class="course-guide-meta__label">' +
      escapeHtml(labels.total) +
      '</span><strong class="course-guide-meta__value">' +
      escapeHtml(meta.totalTime) +
      "</strong></div></div>" +
      '<div class="course-guide-meta__item"><span class="course-guide-meta__icon">' +
      icon("stops") +
      '</span><div class="course-guide-meta__text"><span class="course-guide-meta__label">' +
      escapeHtml(labels.stops) +
      '</span><strong class="course-guide-meta__value">' +
      escapeHtml(meta.stopCount) +
      "</strong></div></div>" +
      '<div class="course-guide-meta__item"><span class="course-guide-meta__icon">' +
      icon("start") +
      '</span><div class="course-guide-meta__text"><span class="course-guide-meta__label">' +
      escapeHtml(labels.start) +
      '</span><strong class="course-guide-meta__value">' +
      escapeHtml(meta.firstTime) +
      "</strong></div></div>" +
      '<div class="course-guide-meta__item"><span class="course-guide-meta__icon">' +
      icon("finish") +
      '</span><div class="course-guide-meta__text"><span class="course-guide-meta__label">' +
      escapeHtml(labels.finish) +
      '</span><strong class="course-guide-meta__value">' +
      escapeHtml(meta.lastTime) +
      "</strong></div></div>" +
      "</div>"
    );
  }

  function routePoints(course, region) {
    var index = placeIndex();
    var points = [];
    var seen = {};
    (course.stops || []).forEach(function (stop, idx) {
      var sc = stopCopy(region, course.id, idx);
      var hit =
        lookupCoord(stop.place, index) ||
        lookupCoord(imageSlug(stop.image), index);
      if (hit && typeof hit.lat === "number" && typeof hit.lng === "number") {
        var key = hit.lat.toFixed(4) + "," + hit.lng.toFixed(4);
        if (seen[key]) return;
        seen[key] = true;
        points.push({
          lat: hit.lat,
          lng: hit.lng,
          time: stop.time || "",
          name: sc.name || "",
        });
      }
    });
    return points;
  }

  var SAME_BUILDING = 0.00018;

  function sameBuilding(a, b) {
    return (
      Math.abs(a.lat - b.lat) < SAME_BUILDING &&
      Math.abs(a.lng - b.lng) < SAME_BUILDING
    );
  }

  function canvasVisible(canvas) {
    if (!canvas || !document.contains(canvas)) return false;
    if (canvas.closest("[hidden]")) return false;
    return canvas.clientWidth > 8 && canvas.clientHeight > 8;
  }

  function disconnectMapWatchers(map, canvas) {
    if (map && map.__courseRo) {
      try {
        map.__courseRo.disconnect();
      } catch (e) {
        /* ignore */
      }
      map.__courseRo = null;
    }
    if (canvas && canvas.__courseIo) {
      try {
        canvas.__courseIo.disconnect();
      } catch (e) {
        /* ignore */
      }
      canvas.__courseIo = null;
    }
  }

  function fitCourseMap(map) {
    if (!map || !map.__courseBounds) return;
    try {
      map.invalidateSize();
      if (map.__courseBounds.isValid && map.__courseBounds.isValid()) {
        map.fitBounds(map.__courseBounds, { padding: [36, 36], maxZoom: 15 });
      }
    } catch (e) {
      /* ignore */
    }
  }

  function destroyMaps(root) {
    var maps = [];
    var scope = root || document;
    if (scope.querySelectorAll) {
      scope.querySelectorAll("[data-course-map]").forEach(function (canvas) {
        disconnectMapWatchers(canvas.__leafletMap, canvas);
      });
    }
    if (root) {
      maps = root.__courseMaps || [];
      root.__courseMaps = [];
    } else {
      maps = liveMaps.slice();
      liveMaps = [];
      document.querySelectorAll(ROOT_SEL).forEach(function (el) {
        maps = maps.concat(el.__courseMaps || []);
        el.__courseMaps = [];
      });
    }
    maps.forEach(function (map) {
      disconnectMapWatchers(map, map.getContainer && map.getContainer());
      try {
        map.remove();
      } catch (e) {
        /* ignore */
      }
    });
  }

  function mountRouteMap(host) {
    if (typeof window.L === "undefined") return;
    var canvas = host.querySelector("[data-course-map]");
    if (!canvas) return;
    var raw = canvas.getAttribute("data-points") || "[]";
    var points = [];
    try {
      points = JSON.parse(raw);
    } catch (e) {
      return;
    }
    if (points.length < 2) return;

    function watchUntilVisible() {
      if (canvas.__courseIo || typeof IntersectionObserver === "undefined") {
        return;
      }
      var io = new IntersectionObserver(function () {
        if (!canvasVisible(canvas)) return;
        io.disconnect();
        canvas.__courseIo = null;
        mountRouteMap(host);
      });
      canvas.__courseIo = io;
      io.observe(canvas);
    }

    if (canvas.__leafletMap) {
      if (canvasVisible(canvas)) fitCourseMap(canvas.__leafletMap);
      else watchUntilVisible();
      return;
    }

    if (!canvasVisible(canvas)) {
      watchUntilVisible();
      return;
    }

    var map = window.L.map(canvas, {
      scrollWheelZoom: false,
      zoomControl: true,
      attributionControl: true,
    });
    canvas.__leafletMap = map;
    window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: "&copy; OpenStreetMap",
    }).addTo(map);

    var latlngs = points.map(function (p) {
      return [p.lat, p.lng];
    });
    map.__courseBounds = window.L.latLngBounds(latlngs);
    window.L.polyline(latlngs, {
      color: "#ffffff",
      weight: 8,
      opacity: 0.7,
      lineJoin: "round",
      lineCap: "round",
    }).addTo(map);
    var routeLine = window.L.polyline(latlngs, {
      color: "#1f5fe0",
      weight: 5,
      opacity: 0.95,
      lineJoin: "round",
      lineCap: "round",
    }).addTo(map);

    var pinLayer = window.L.layerGroup().addTo(map);

    function renderPins() {
      pinLayer.clearLayers();
      var items = points.map(function (p, idx) {
        return {
          lat: p.lat,
          lng: p.lng,
          num: idx + 1,
          name: p.name,
          time: p.time,
        };
      });
      var used = {};
      items.forEach(function (p, i) {
        if (used[i]) return;
        var group = [i];
        used[i] = true;
        items.forEach(function (q, j) {
          if (used[j]) return;
          if (sameBuilding(p, q)) {
            group.push(j);
            used[j] = true;
          }
        });
        group.forEach(function (gi, k) {
          var item = items[gi];
          var dx = 0;
          var dy = 0;
          if (group.length > 1) {
            var angle = (Math.PI * 2 * k) / group.length - Math.PI / 2;
            dx = Math.cos(angle) * 10;
            dy = Math.sin(angle) * 10;
          }
          var marker = window.L.marker([item.lat, item.lng], {
            zIndexOffset: item.num * 40,
            icon: window.L.divIcon({
              className: "course-guide-map-pin" + (item.num % 2 ? "" : " is-alt"),
              html: "<span>" + item.num + "</span>",
              iconSize: [28, 28],
              iconAnchor: [14 - dx, 14 - dy],
            }),
          });
          marker.bindPopup(
            "<strong>" +
              escapeHtml(item.name) +
              "</strong>" +
              (item.time ? "<br>" + escapeHtml(item.time) : "")
          );
          pinLayer.addLayer(marker);
        });
      });
      if (pinLayer.bringToFront) pinLayer.bringToFront();
    }

    fitCourseMap(map);
    renderPins();
    var owner =
      host.closest("[data-region-curated], [data-seoul-curated]") || null;
    if (owner) {
      owner.__courseMaps = owner.__courseMaps || [];
      owner.__courseMaps.push(map);
    } else {
      liveMaps.push(map);
    }
    if (typeof ResizeObserver !== "undefined") {
      var ro = new ResizeObserver(function () {
        if (!canvasVisible(canvas)) return;
        fitCourseMap(map);
      });
      map.__courseRo = ro;
      ro.observe(canvas);
    }
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        try {
          fitCourseMap(map);
          if (routeLine.bringToFront) routeLine.bringToFront();
          renderPins();
        } catch (e) {
          /* ignore */
        }
      });
    });
  }

  function revealVisibleMaps() {
    document.querySelectorAll("[data-course-map]").forEach(function (canvas) {
      if (!canvasVisible(canvas)) return;
      if (canvas.__leafletMap) {
        fitCourseMap(canvas.__leafletMap);
        return;
      }
      var host =
        canvas.closest("[data-seoul-detail-host]") ||
        canvas.closest(ROOT_SEL);
      if (host) mountRouteMap(host);
    });
  }

  function renderRouteMap(course, region) {
    var points = routePoints(course, region);
    var label = t("travelCourses.seoulCurated.fullRouteLabel", "지도상 이동 경로");
    if (points.length < 2) return "";
    var legend = points
      .map(function (p, idx) {
        return (
          '<li class="course-guide-map__legend-item">' +
          '<span class="course-guide-map__legend-num">' +
          (idx + 1) +
          "</span>" +
          '<span class="course-guide-map__legend-copy">' +
          (p.time
            ? '<em>' + escapeHtml(p.time) + "</em>"
            : "") +
          escapeHtml(p.name) +
          "</span></li>"
        );
      })
      .join("");
    return (
      '<section class="course-guide-map">' +
      '<h4 class="course-guide-map__title">' +
      '<span class="course-guide-section-icon" aria-hidden="true"><svg viewBox="0 0 20 20"><path d="M10 17s5-4.4 5-8.2A5 5 0 0 0 5 8.8C5 12.6 10 17 10 17z"></path><circle cx="10" cy="8.6" r="1.7"></circle></svg></span>' +
      escapeHtml(label) +
      "</h4>" +
      '<div class="course-guide-map__layout">' +
      '<div class="course-guide-map__canvas" data-course-map data-points="' +
      escapeAttr(JSON.stringify(points)) +
      '"></div>' +
      '<ol class="course-guide-map__legend">' +
      legend +
      "</ol></div></section>"
    );
  }

  function renderStop(stop, sc, idx) {
    var n = idx + 1;
    var odd = idx % 2 === 0;
    var hasImg = !!(stop.image && String(stop.image).trim());
    var media = hasImg
      ? '<figure class="course-guide-stop__media">' +
        '<img class="course-guide-thumb" src="' +
        escapeAttr(imgSrc(stop.image)) +
        '" alt="" loading="lazy" decoding="async" onerror="this.onerror=null;this.src=\'../../Images/travel-courses/_fallback.jpg\'">' +
        "</figure>"
      : "";
    var copy =
      '<div class="course-guide-stop__copy">' +
      (stop.time
        ? '<span class="course-guide-stop__time">' +
          escapeHtml(stop.time) +
          "</span>"
        : "") +
      '<h4 class="course-guide-stop__name">' +
      escapeHtml(sc.name) +
      "</h4>" +
      (sc.desc
        ? '<p class="course-guide-stop__desc">' + escapeHtml(sc.desc) + "</p>"
        : "") +
      "</div>";
    return (
      '<li class="course-guide-stop ' +
      (odd ? "is-odd" : "is-even") +
      (idx === 0 ? " is-first" : "") +
      '">' +
      '<div class="course-guide-stop__stack">' +
      media +
      copy +
      "</div>" +
      '<div class="course-guide-stop__rail" aria-hidden="true">' +
      '<span class="course-guide-stop__dot">' +
      n +
      "</span></div></li>"
    );
  }

  function renderDetail(host, course, region) {
    if (!course) return;
    var root = host.closest(ROOT_SEL);
    destroyMaps(root);
    var copy = courseCopy(region, course.id);
    var chrome = chromeCopy(region);
    var tipsLabel = t("travelCourses.seoulCurated.tipsLabel", "팁");
    var routeLabel = t(
      "travelCourses.seoulCurated.routeLabel",
      "한눈에 보는 루트"
    );
    var scheduleLabel = t(
      "travelCourses.seoulCurated.scheduleLabel",
      "하루 일정"
    );
    var items = (course.stops || [])
      .map(function (stop, idx) {
        return renderStop(stop, stopCopy(region, course.id, idx), idx);
      })
      .join("");

    host.innerHTML =
      '<article class="course-guide-detail" data-seoul-detail>' +
      '<header class="course-guide-hero">' +
      '<img class="course-guide-hero__img" src="' +
      escapeAttr(imgSrc(course.cover)) +
      '" alt="" loading="lazy" decoding="async" onerror="this.onerror=null;this.src=\'../../Images/travel-courses/_fallback.jpg\'">' +
      '<div class="course-guide-hero__shade" aria-hidden="true"></div>' +
      '<div class="course-guide-hero__text">' +
      '<p class="course-guide-detail__eyebrow">' +
      escapeHtml(chrome.guideEyebrow) +
      "</p>" +
      '<h3 class="course-guide-detail__title">' +
      escapeHtml(copy.title) +
      "</h3>" +
      (mobilityKind(course)
        ? '<p class="course-guide-detail__mob">' +
          mobilityBadgeHtml(mobilityKind(course), false) +
          "</p>"
        : "") +
      "</div></header>" +
      '<div class="course-guide-detail__body">' +
      (copy.summary
        ? '<p class="course-guide-detail__summary">' +
          escapeHtml(copy.summary) +
          "</p>"
        : "") +
      noticeHtml(copy) +
      renderMetaCards(course) +
      renderAside(copy, routeLabel, tipsLabel) +
      '<section class="course-guide-schedule">' +
      '<h4 class="course-guide-schedule__title">' +
      '<span class="course-guide-section-icon" aria-hidden="true"><svg viewBox="0 0 20 20"><path d="M4 3.5h12v13H4z"></path><path d="M7 2.5v2M13 2.5v2M4 7.5h12"></path></svg></span>' +
      escapeHtml(scheduleLabel) +
      "</h4>" +
      '<ol class="course-guide-timeline">' +
      items +
      "</ol></section>" +
      renderRouteMap(course, region) +
      "</div></article>";

    mountRouteMap(host);
  }

  function renderEmpty(root, region) {
    destroyMaps(root);
    var chrome = chromeCopy(region);
    var name = regionLabel(region);
    var coming = fillRegion(
      t(
        "travelCourses.regionComingSoon",
        "{region} 추천 코스는 추후 추가될 예정입니다."
      ),
      name
    );
    var schedule = t(
      "travelCourses.scheduleComingSoon",
      "당일·1박2일 등 일정별 코스는 추후 추가될 예정입니다."
    );
    root.innerHTML =
      '<div class="course-guide">' +
      '<p class="course-guide__intro">' +
      escapeHtml(chrome.intro) +
      "</p>" +
      '<div class="travel-course-empty" role="status">' +
      '<p class="travel-course-empty__lead">' +
      escapeHtml(coming) +
      "</p>" +
      '<p class="travel-course-empty__note">' +
      escapeHtml(schedule) +
      "</p>" +
      "</div></div>";
  }

  function courseOptionHtml(c, region, activeId) {
    var title = courseCopy(region, c.id).title;
    var mob = mobilityKind(c) ? " · " + mobilityLabel(mobilityKind(c), true) : "";
    return (
      '<option value="' +
      escapeAttr(c.id) +
      '"' +
      (c.id === activeId ? " selected" : "") +
      ">" +
      escapeHtml(title + mob) +
      "</option>"
    );
  }

  function courseChipHtml(c, num, region, activeId) {
    var title = courseCopy(region, c.id).title;
    var mob = mobilityKind(c) ? mobilityBadgeHtml(mobilityKind(c), true) : "";
    return (
      '<button type="button" class="course-guide-chip' +
      (c.id === activeId ? " is-active" : "") +
      '" data-seoul-course="' +
      escapeAttr(c.id) +
      '" aria-pressed="' +
      (c.id === activeId ? "true" : "false") +
      '"><span class="course-guide-chip__num">' +
      num +
      '</span><span class="course-guide-chip__label">' +
      escapeHtml(title) +
      "</span>" +
      mob +
      "</button>"
    );
  }

  function renderCourseOptions(list, region, activeId) {
    return list
      .map(function (c) {
        return courseOptionHtml(c, region, activeId);
      })
      .join("");
  }

  function renderCourseChips(list, region, activeId) {
    return list
      .map(function (c, idx) {
        return courseChipHtml(c, idx + 1, region, activeId);
      })
      .join("");
  }

  function render(root) {
    var region = regionId(root);
    var list = coursesFor(region);
    if (!list.length) {
      renderEmpty(root, region);
      return;
    }

    var chrome = chromeCopy(region);
    var pickLabel = chrome.pickLabel;
    var intro = chrome.intro;
    var activeId =
      root.getAttribute("data-active-course") || (list[0] && list[0].id) || "";

    var options = renderCourseOptions(list, region, activeId);
    var chips = renderCourseChips(list, region, activeId);

    destroyMaps(root);
    root.innerHTML =
      '<div class="course-guide">' +
      '<p class="course-guide__intro">' +
      escapeHtml(intro) +
      "</p>" +
      '<label class="cat-select-wrap course-guide-select-wrap">' +
      '<span class="cat-select-label">' +
      escapeHtml(pickLabel) +
      "</span>" +
      '<select class="cat-select" data-seoul-course-select aria-label="' +
      escapeAttr(pickLabel) +
      '">' +
      options +
      "</select></label>" +
      '<div class="course-guide-chips" role="listbox" aria-label="' +
      escapeAttr(pickLabel) +
      '">' +
      chips +
      "</div>" +
      '<div class="course-guide-detail-host" data-seoul-detail-host></div></div>';

    var detailHost = root.querySelector("[data-seoul-detail-host]");
    var active =
      list.filter(function (c) {
        return c.id === activeId;
      })[0] || list[0];
    renderDetail(detailHost, active, region);

    var select = root.querySelector("[data-seoul-course-select]");
    if (select) {
      select.addEventListener("change", function () {
        root.setAttribute("data-active-course", select.value);
        render(root);
        root.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
    root.querySelectorAll("[data-seoul-course]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        root.setAttribute(
          "data-active-course",
          btn.getAttribute("data-seoul-course")
        );
        render(root);
      });
    });
  }

  function refreshAll() {
    document.querySelectorAll(ROOT_SEL).forEach(function (root) {
      render(root);
    });
  }

  function init() {
    refreshAll();
    document.addEventListener("guide:langchange", refreshAll);
    document.addEventListener("guide:tabschange", function () {
      setTimeout(revealVisibleMaps, 40);
    });
    window.addEventListener("hashchange", function () {
      setTimeout(revealVisibleMaps, 40);
    });
    setTimeout(revealVisibleMaps, 40);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

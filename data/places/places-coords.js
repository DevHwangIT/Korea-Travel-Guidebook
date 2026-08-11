/**
 * Lat/lng for guidebook places (pages/transportation/places/{slug}/).
 * Approximate center points for known landmarks / districts — not GPS survey data.
 * Used by js/places-map.js (immersive Korea peninsula map).
 *
 * type: "city" | "nature" | "heritage" | "airport" | "info"
 *   city     — urban nightlife / shopping / modern landmarks
 *   nature   — mountains, beaches, parks, scenic outdoors
 *   heritage — palaces, temples, historic / cultural villages
 *   airport  — major passenger airports (plane icon on map)
 *   info     — embassies / visitor help centers (muted secondary badge)
 */
window.PLACES_COORDS = [
  { slug: "myeongdong", lat: 37.5636, lng: 126.9869, region: "seoul", type: "city", note: "Myeongdong shopping street" },
  { slug: "gyeongbok", lat: 37.5796, lng: 126.977, region: "seoul", type: "heritage", note: "Gyeongbokgung Palace" },
  { slug: "gangnam", lat: 37.4979, lng: 127.0276, region: "seoul", type: "city", note: "Gangnam Station area" },
  { slug: "hongdae", lat: 37.5563, lng: 126.9236, region: "seoul", type: "city", note: "Hongik University / Hongdae" },
  { slug: "itaewon", lat: 37.5345, lng: 126.9946, region: "seoul", type: "city", note: "Itaewon Station area" },
  { slug: "suwon", lat: 37.2851, lng: 127.0115, region: "gyeonggi", type: "heritage", note: "Suwon Hwaseong Fortress" },
  { slug: "goyang", lat: 37.658, lng: 126.769, region: "gyeonggi", type: "nature", note: "Ilsan Lake Park" },
  { slug: "gapyeong", lat: 37.7915, lng: 127.5258, region: "gyeonggi", type: "nature", note: "Nami Island / Gapyeong" },
  { slug: "haeundae", lat: 35.1587, lng: 129.1604, region: "busan", type: "nature", note: "Haeundae Beach" },
  { slug: "nampo", lat: 35.0969, lng: 129.0306, region: "busan", type: "city", note: "Jagalchi / Nampo" },
  { slug: "seomyeon", lat: 35.1576, lng: 129.0595, region: "busan", type: "city", note: "Seomyeon, Busan" },
  { slug: "namsan", lat: 37.5512, lng: 126.9882, region: "seoul", type: "city", note: "N Seoul Tower / Namsan" },
  { slug: "bukchon", lat: 37.5826, lng: 126.9831, region: "seoul", type: "heritage", note: "Bukchon Hanok Village" },
  { slug: "insadong", lat: 37.5717, lng: 126.9858, region: "seoul", type: "heritage", note: "Insadong" },
  { slug: "dongdaemun", lat: 37.5668, lng: 127.0094, region: "seoul", type: "city", note: "Dongdaemun Design Plaza (DDP)" },
  { slug: "lotte-tower", lat: 37.5126, lng: 127.1025, region: "seoul", type: "city", note: "Lotte World Tower / Seoul Sky" },
  { slug: "songdo", lat: 37.3928, lng: 126.6388, region: "incheon", type: "city", note: "Songdo Central Park" },
  { slug: "seoraksan", lat: 38.1195, lng: 128.4654, region: "gangwon", type: "nature", note: "Seoraksan National Park" },
  { slug: "bulguksa", lat: 35.79, lng: 129.332, region: "gyeongju", type: "heritage", note: "Bulguksa Temple" },
  { slug: "donggung", lat: 35.8347, lng: 129.2268, region: "gyeongju", type: "heritage", note: "Donggung Palace and Wolji Pond" },
  { slug: "jeonju", lat: 35.815, lng: 127.153, region: "jeolla", type: "heritage", note: "Jeonju Hanok Village" },
  { slug: "seongsan", lat: 33.4581, lng: 126.9425, region: "jeju", type: "nature", note: "Seongsan Ilchulbong" },
  { slug: "jungmun", lat: 33.2427, lng: 126.4127, region: "jeju", type: "nature", note: "Jungmun / Seogwipo tourist belt" },
  { slug: "gamcheon", lat: 35.0975, lng: 129.0104, region: "busan", type: "heritage", note: "Gamcheon Culture Village" },
  { slug: "haedong", lat: 35.1884, lng: 129.2233, region: "busan", type: "heritage", note: "Haedong Yonggungsa Temple" },
  { slug: "imjingak", lat: 37.8892, lng: 126.7403, region: "gyeonggi", type: "heritage", note: "Imjingak (DMZ tourist area)" },
  { slug: "everland", lat: 37.294, lng: 127.2023, region: "gyeonggi", type: "city", note: "Everland" },
  { slug: "airport-icn", lat: 37.4602, lng: 126.4407, region: "incheon", type: "airport", note: "Incheon Intl (ICN)" },
  { slug: "airport-gmp", lat: 37.5583, lng: 126.7906, region: "seoul", type: "airport", note: "Gimpo Intl (GMP)" },
  { slug: "airport-pus", lat: 35.1795, lng: 128.9382, region: "busan", type: "airport", note: "Gimhae Intl (PUS)" },
  { slug: "airport-cju", lat: 33.5113, lng: 126.493, region: "jeju", type: "airport", note: "Jeju Intl (CJU)" },
  { slug: "airport-tae", lat: 35.8941, lng: 128.6589, region: "", type: "airport", note: "Daegu Intl (TAE)" },
  { slug: "airport-cjj", lat: 36.7166, lng: 127.4989, region: "", type: "airport", note: "Cheongju Intl (CJJ)" },
  /* Useful-info markers (secondary badge style — not primary sightseeing pins) */
  { slug: "seoul-global-center", lat: 37.5665, lng: 126.9778, region: "seoul", type: "info", note: "Seoul Global Center" },
  { slug: "tourist-info-myeongdong", lat: 37.5609, lng: 126.986, region: "seoul", type: "info", note: "Myeongdong Tourist Information" },
  { slug: "embassy-us-seoul", lat: 37.5735, lng: 126.9769, region: "seoul", type: "info", note: "U.S. Embassy Seoul" },
  { slug: "embassy-japan-seoul", lat: 37.5752, lng: 126.9834, region: "seoul", type: "info", note: "Embassy of Japan in Seoul" },
  { slug: "embassy-china-seoul", lat: 37.5669, lng: 126.9794, region: "seoul", type: "info", note: "Embassy of China in Seoul" },
  /* Added famous nationwide spots */
  { slug: "noryangjin-cupbap", lat: 37.5133, lng: 126.944, region: "seoul", type: "city", note: "Noryangjin Cupbap Street" },
  { slug: "hangang-yeouido", lat: 37.5285, lng: 126.934, region: "seoul", type: "nature", note: "Yeouido Hangang Park" },
  { slug: "hangang-banpo", lat: 37.5105, lng: 126.996, region: "seoul", type: "nature", note: "Banpo Hangang Park" },
  { slug: "hallasan", lat: 33.3617, lng: 126.5292, region: "jeju", type: "nature", note: "Hallasan" },
  { slug: "cheonjeyeon", lat: 33.2468, lng: 126.5544, region: "jeju", type: "nature", note: "Cheonjeyeon Falls" },
  { slug: "biff-square", lat: 35.0986, lng: 129.0306, region: "busan", type: "city", note: "BIFF Square" },
  { slug: "hwangnidan", lat: 35.8362, lng: 129.2115, region: "gyeongju", type: "heritage", note: "Hwangnidan-gil" },
  { slug: "hahoe", lat: 36.5391, lng: 128.5178, region: "gyeongsang", type: "heritage", note: "Andong Hahoe Village" },
  { slug: "boseong", lat: 34.714, lng: 127.081, region: "jeolla", type: "nature", note: "Boseong green tea" },
  { slug: "suncheon-bay", lat: 34.882, lng: 127.512, region: "jeolla", type: "nature", note: "Suncheon Bay" },
  { slug: "tongyeong", lat: 34.8544, lng: 128.433, region: "gyeongsang", type: "city", note: "Tongyeong" },
  { slug: "ulsan-daewangam", lat: 35.492, lng: 129.44, region: "gyeongsang", type: "nature", note: "Ulsan Daewangam Park" },
  { slug: "zz-verify-place", lat: 36.5, lng: 127.8, region: "seoul", type: "city", note: "검증명소" }
];

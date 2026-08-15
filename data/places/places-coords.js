/**
 * Lat/lng for guidebook places (pages/transportation/places/{slug}/).
 * Approximate center points for known landmarks / districts — not GPS survey data.
 * Used by js/places-map.js (immersive Korea peninsula map).
 *
 * type: "city" | "nature" | "heritage" | "airport" | "info" | "locker" | "port" | "bus-terminal"
 *   city     — urban nightlife / shopping / modern landmarks
 *   nature   — mountains, beaches, parks, scenic outdoors
 *   heritage — palaces, temples, historic / cultural villages
 *   airport  — major passenger airports (plane icon on map)
 *   info     — embassies / visitor help centers (muted secondary badge)
 *   locker   — luggage storage / coin lockers (station & airport)
 *   port     — major harbors / passenger ferry terminals
 *   bus-terminal — major express / intercity bus terminals
 *
 * image: local real photograph under Images/places/{slug}.jpg (Wikimedia Commons / free licenses).
 *        Type fallbacks in Images/places/_types/ are last-resort only.
 */
window.PLACES_COORDS = [
  { slug: "myeongdong", lat: 37.5636, lng: 126.9869, region: "seoul", type: "city", note: "Myeongdong shopping street", image: "Images/places/myeongdong.jpg" },
  { slug: "gyeongbok", lat: 37.5796, lng: 126.977, region: "seoul", type: "heritage", note: "Gyeongbokgung Palace", image: "Images/places/gyeongbok.jpg" },
  { slug: "gangnam", lat: 37.4979, lng: 127.0276, region: "seoul", type: "city", note: "Gangnam Station area", image: "Images/places/gangnam.jpg" },
  { slug: "hongdae", lat: 37.5563, lng: 126.9236, region: "seoul", type: "city", note: "Hongik University / Hongdae", image: "Images/places/hongdae.jpg" },
  { slug: "itaewon", lat: 37.5345, lng: 126.9946, region: "seoul", type: "city", note: "Itaewon Station area", image: "Images/places/itaewon.jpg" },
  { slug: "suwon", lat: 37.2851, lng: 127.0115, region: "gyeonggi", type: "heritage", note: "Suwon Hwaseong Fortress", image: "Images/places/suwon.jpg" },
  { slug: "goyang", lat: 37.658, lng: 126.769, region: "gyeonggi", type: "nature", note: "Ilsan Lake Park", image: "Images/places/goyang.jpg" },
  { slug: "gapyeong", lat: 37.7915, lng: 127.5258, region: "gyeonggi", type: "nature", note: "Nami Island / Gapyeong", image: "Images/places/gapyeong.jpg" },
  { slug: "haeundae", lat: 35.1587, lng: 129.1604, region: "busan", type: "nature", note: "Haeundae Beach", image: "Images/places/haeundae.jpg" },
  { slug: "nampo", lat: 35.0969, lng: 129.0306, region: "busan", type: "city", note: "Jagalchi / Nampo", image: "Images/places/nampo.jpg" },
  { slug: "seomyeon", lat: 35.1576, lng: 129.0595, region: "busan", type: "city", note: "Seomyeon, Busan", image: "Images/places/seomyeon.jpg" },
  { slug: "namsan", lat: 37.5512, lng: 126.9882, region: "seoul", type: "city", note: "N Seoul Tower / Namsan", image: "Images/places/namsan.jpg" },
  { slug: "bukchon", lat: 37.5826, lng: 126.9831, region: "seoul", type: "heritage", note: "Bukchon Hanok Village", image: "Images/places/bukchon.jpg" },
  { slug: "insadong", lat: 37.5717, lng: 126.9858, region: "seoul", type: "heritage", note: "Insadong", image: "Images/places/insadong.jpg" },
  { slug: "dongdaemun", lat: 37.5668, lng: 127.0094, region: "seoul", type: "city", note: "Dongdaemun Design Plaza (DDP)", image: "Images/places/dongdaemun.jpg" },
  { slug: "lotte-tower", lat: 37.5126, lng: 127.1025, region: "seoul", type: "city", note: "Lotte World Tower / Seoul Sky", image: "Images/places/lotte-tower.jpg" },
  { slug: "songdo", lat: 37.3928, lng: 126.6388, region: "incheon", type: "city", note: "Songdo Central Park", image: "Images/places/songdo.jpg" },
  { slug: "seoraksan", lat: 38.1195, lng: 128.4654, region: "gangwon", type: "nature", note: "Seoraksan National Park", image: "Images/places/seoraksan.jpg" },
  { slug: "bulguksa", lat: 35.79, lng: 129.332, region: "gyeongju", type: "heritage", note: "Bulguksa Temple", image: "Images/places/bulguksa.jpg" },
  { slug: "donggung", lat: 35.8347, lng: 129.2268, region: "gyeongju", type: "heritage", note: "Donggung Palace and Wolji Pond", image: "Images/places/donggung.jpg" },
  { slug: "jeonju", lat: 35.815, lng: 127.153, region: "jeolla", type: "heritage", note: "Jeonju Hanok Village", image: "Images/places/jeonju.jpg" },
  { slug: "seongsan", lat: 33.4581, lng: 126.9425, region: "jeju", type: "nature", note: "Seongsan Ilchulbong", image: "Images/places/seongsan.jpg" },
  { slug: "jungmun", lat: 33.2427, lng: 126.4127, region: "jeju", type: "nature", note: "Jungmun / Seogwipo tourist belt", image: "Images/places/jungmun.jpg" },
  { slug: "gamcheon", lat: 35.0975, lng: 129.0104, region: "busan", type: "heritage", note: "Gamcheon Culture Village", image: "Images/places/gamcheon.jpg" },
  { slug: "haedong", lat: 35.1884, lng: 129.2233, region: "busan", type: "heritage", note: "Haedong Yonggungsa Temple", image: "Images/places/haedong.jpg" },
  { slug: "imjingak", lat: 37.8892, lng: 126.7403, region: "gyeonggi", type: "heritage", note: "Imjingak (DMZ tourist area)", image: "Images/places/imjingak.jpg" },
  { slug: "everland", lat: 37.294, lng: 127.2023, region: "gyeonggi", type: "city", note: "Everland", image: "Images/places/everland.jpg" },
  { slug: "airport-icn", lat: 37.4602, lng: 126.4407, region: "incheon", type: "airport", note: "Incheon Intl (ICN)", image: "Images/places/airport-icn.jpg" },
  { slug: "airport-gmp", lat: 37.5583, lng: 126.7906, region: "seoul", type: "airport", note: "Gimpo Intl (GMP)", image: "Images/places/airport-gmp.jpg" },
  { slug: "airport-pus", lat: 35.1795, lng: 128.9382, region: "busan", type: "airport", note: "Gimhae Intl (PUS)", image: "Images/places/airport-pus.jpg" },
  { slug: "airport-cju", lat: 33.5113, lng: 126.493, region: "jeju", type: "airport", note: "Jeju Intl (CJU)", image: "Images/places/airport-cju.jpg" },
  { slug: "airport-tae", lat: 35.8941, lng: 128.6589, region: "", type: "airport", note: "Daegu Intl (TAE)", image: "Images/places/airport-tae.jpg" },
  { slug: "airport-cjj", lat: 36.7166, lng: 127.4989, region: "", type: "airport", note: "Cheongju Intl (CJJ)", image: "Images/places/airport-cjj.jpg" },
  /* Useful-info markers (secondary badge style — not primary sightseeing pins) */
  { slug: "seoul-global-center", lat: 37.5665, lng: 126.9778, region: "seoul", type: "info", note: "Seoul Global Center", image: "Images/places/seoul-global-center.jpg" },
  { slug: "tourist-info-myeongdong", lat: 37.5609, lng: 126.986, region: "seoul", type: "info", note: "Myeongdong Tourist Information", image: "Images/places/tourist-info-myeongdong.jpg" },
  { slug: "embassy-us-seoul", lat: 37.5735, lng: 126.9769, region: "seoul", type: "info", note: "U.S. Embassy Seoul", image: "Images/places/embassy-us-seoul.jpg" },
  { slug: "embassy-japan-seoul", lat: 37.5752, lng: 126.9834, region: "seoul", type: "info", note: "Embassy of Japan in Seoul", image: "Images/places/embassy-japan-seoul.jpg" },
  { slug: "embassy-china-seoul", lat: 37.5669, lng: 126.9794, region: "seoul", type: "info", note: "Embassy of China in Seoul", image: "Images/places/embassy-china-seoul.jpg" },
  /* Added famous nationwide spots */
  { slug: "noryangjin-cupbap", lat: 37.5133, lng: 126.944, region: "seoul", type: "city", note: "Noryangjin Cupbap Street", image: "Images/places/noryangjin-cupbap.jpg" },
  { slug: "hangang-yeouido", lat: 37.5285, lng: 126.934, region: "seoul", type: "nature", note: "Yeouido Hangang Park", image: "Images/places/hangang-yeouido.jpg" },
  { slug: "hangang-banpo", lat: 37.5105, lng: 126.996, region: "seoul", type: "nature", note: "Banpo Hangang Park", image: "Images/places/hangang-banpo.jpg" },
  { slug: "hallasan", lat: 33.3617, lng: 126.5292, region: "jeju", type: "nature", note: "Hallasan", image: "Images/places/hallasan.jpg" },
  { slug: "cheonjeyeon", lat: 33.2468, lng: 126.5544, region: "jeju", type: "nature", note: "Cheonjeyeon Falls", image: "Images/places/cheonjeyeon.jpg" },
  { slug: "biff-square", lat: 35.0986, lng: 129.0306, region: "busan", type: "city", note: "BIFF Square", image: "Images/places/biff-square.jpg" },
  { slug: "hwangnidan", lat: 35.8362, lng: 129.2115, region: "gyeongju", type: "heritage", note: "Hwangnidan-gil", image: "Images/places/hwangnidan.jpg" },
  { slug: "hahoe", lat: 36.5391, lng: 128.5178, region: "gyeongsang", type: "heritage", note: "Andong Hahoe Village", image: "Images/places/hahoe.jpg" },
  { slug: "boseong", lat: 34.714, lng: 127.081, region: "jeolla", type: "nature", note: "Boseong green tea", image: "Images/places/boseong.jpg" },
  { slug: "suncheon-bay", lat: 34.882, lng: 127.512, region: "jeolla", type: "nature", note: "Suncheon Bay", image: "Images/places/suncheon-bay.jpg" },
  { slug: "tongyeong", lat: 34.8544, lng: 128.433, region: "gyeongsang", type: "city", note: "Tongyeong", image: "Images/places/tongyeong.jpg" },
  { slug: "ulsan-daewangam", lat: 35.492, lng: 129.44, region: "gyeongsang", type: "nature", note: "Ulsan Daewangam Park", image: "Images/places/ulsan-daewangam.jpg" },
  { slug: "locker-seoul-station", lat: 37.5547, lng: 126.9707, region: "seoul", type: "locker", note: "Seoul Station luggage lockers", image: "Images/places/locker-seoul-station.jpg" },
  { slug: "locker-yongsan-station", lat: 37.5299, lng: 126.9648, region: "seoul", type: "locker", note: "Yongsan Station lockers", image: "Images/places/locker-yongsan-station.jpg" },
  { slug: "locker-busan-station", lat: 35.1152, lng: 129.0413, region: "busan", type: "locker", note: "Busan Station lockers", image: "Images/places/locker-busan-station.jpg" },
  { slug: "locker-myeongdong-station", lat: 37.5609, lng: 126.9863, region: "seoul", type: "locker", note: "Myeongdong Station T-locker", image: "Images/places/locker-myeongdong-station.jpg" },
  { slug: "locker-hongdae-station", lat: 37.5572, lng: 126.9254, region: "seoul", type: "locker", note: "Hongdae Station T-locker", image: "Images/places/locker-hongdae-station.jpg" },
  { slug: "locker-gangnam-station", lat: 37.4979, lng: 127.0276, region: "seoul", type: "locker", note: "Gangnam Station T-locker", image: "Images/places/locker-gangnam-station.jpg" },
  { slug: "locker-express-bus-terminal", lat: 37.5046, lng: 127.0045, region: "seoul", type: "locker", note: "Express Bus Terminal lockers", image: "Images/places/locker-express-bus-terminal.jpg" },
  { slug: "locker-icn-t1", lat: 37.4474, lng: 126.4525, region: "incheon", type: "locker", note: "ICN T1 luggage storage", image: "Images/places/locker-icn-t1.jpg" },
  { slug: "locker-icn-t2", lat: 37.4689, lng: 126.4335, region: "incheon", type: "locker", note: "ICN T2 luggage storage", image: "Images/places/locker-icn-t2.jpg" },
  { slug: "locker-dongdaemun-station", lat: 37.5656, lng: 127.009, region: "seoul", type: "locker", note: "Dongdaemun History Culture Park Station lockers", image: "Images/places/locker-dongdaemun-station.jpg" },
  { slug: "locker-haeundae-station", lat: 35.1631, lng: 129.1636, region: "busan", type: "locker", note: "Haeundae Station lockers", image: "Images/places/locker-haeundae-station.jpg" },
  { slug: "port-busan", lat: 35.1028, lng: 129.0403, region: "busan", type: "port", note: "Busan Port passenger terminal", image: "Images/places/port-busan.jpg" },
  { slug: "port-incheon", lat: 37.4536, lng: 126.6149, region: "incheon", type: "port", note: "Incheon Port passenger terminal", image: "Images/places/port-incheon.jpg" },
  { slug: "port-jeju", lat: 33.5172, lng: 126.5263, region: "jeju", type: "port", note: "Jeju Port", image: "Images/places/port-jeju.jpg" },
  { slug: "port-mokpo", lat: 34.7917, lng: 126.3889, region: "jeolla", type: "port", note: "Mokpo Port", image: "Images/places/port-mokpo.jpg" },
  { slug: "port-yeosu", lat: 34.738, lng: 127.745, region: "jeolla", type: "port", note: "Yeosu Port / Expo waterfront", image: "Images/places/port-yeosu.jpg" },
  { slug: "port-pohang", lat: 36.0515, lng: 129.384, region: "gyeongsang", type: "port", note: "Pohang Port / Yeongil Bay", image: "Images/places/port-pohang.jpg" },
  { slug: "bus-terminal-seoul-express", lat: 37.5046, lng: 127.0045, region: "seoul", type: "bus-terminal", note: "Seoul Express Bus Terminal / Central City", image: "Images/places/bus-terminal-seoul-express.jpg" },
  { slug: "bus-terminal-east-seoul", lat: 37.5347, lng: 127.0942, region: "seoul", type: "bus-terminal", note: "East Seoul Bus Terminal", image: "Images/places/bus-terminal-east-seoul.jpg" },
  { slug: "bus-terminal-nambu", lat: 37.485, lng: 127.0162, region: "seoul", type: "bus-terminal", note: "Seoul Nambu Bus Terminal", image: "Images/places/bus-terminal-nambu.jpg" },
  { slug: "bus-terminal-busan", lat: 35.2234, lng: 129.0786, region: "busan", type: "bus-terminal", note: "Busan Central Bus Terminal (Nopo)", image: "Images/places/bus-terminal-busan.jpg" },
  { slug: "bus-terminal-daegu", lat: 35.8795, lng: 128.6284, region: "", type: "bus-terminal", note: "Dongdaegu Complex Transfer Center", image: "Images/places/bus-terminal-daegu.jpg" },
  { slug: "bus-terminal-daejeon", lat: 36.3515, lng: 127.4375, region: "", type: "bus-terminal", note: "Daejeon Complex Terminal", image: "Images/places/bus-terminal-daejeon.jpg" },
  { slug: "bus-terminal-gwangju", lat: 35.1603, lng: 126.882, region: "jeolla", type: "bus-terminal", note: "Gwangju Bus Terminal (U-Square)", image: "Images/places/bus-terminal-gwangju.jpg" },
  { slug: "bus-terminal-incheon", lat: 37.4567, lng: 126.7078, region: "incheon", type: "bus-terminal", note: "Incheon Bus Terminal", image: "Images/places/bus-terminal-incheon.jpg" },
  { slug: "bus-terminal-suwon", lat: 37.2505, lng: 127.02, region: "gyeonggi", type: "bus-terminal", note: "Suwon Bus Terminal", image: "Images/places/bus-terminal-suwon.jpg" },
  { slug: "bus-terminal-jeonju", lat: 35.8415, lng: 127.124, region: "jeolla", type: "bus-terminal", note: "Jeonju Express Bus Terminal", image: "Images/places/bus-terminal-jeonju.jpg" },
  { slug: "bus-terminal-ulsan", lat: 35.5525, lng: 129.339, region: "gyeongsang", type: "bus-terminal", note: "Ulsan Express Bus Terminal", image: "Images/places/bus-terminal-ulsan.jpg" },
  { slug: "bus-terminal-gwangmyeong", lat: 37.4164, lng: 126.8849, region: "gyeonggi", type: "bus-terminal", note: "Near KTX Gwangmyeong — southern Gyeonggi coach access", image: "Images/places/bus-terminal-gwangmyeong.jpg" },
];

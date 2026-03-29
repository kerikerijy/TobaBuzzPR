document.addEventListener('DOMContentLoaded', () => {
            // Intersection Observer for fade-in animations
            const observerOptions = {
                threshold: 0.1
            };

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                    }
                });
            }, observerOptions);

            document.querySelectorAll('.animate-on-scroll, .fade-in').forEach(el => {
                el.classList.add('fade-in');
                observer.observe(el);
            });

            // Directory Filter Logic
            const filterButtons = document.querySelectorAll('.filter-btn');
            const schoolRows = document.querySelectorAll('.school-row');

            filterButtons.forEach(btn => {
                btn.addEventListener('click', () => {
                    filterButtons.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');

                    const filter = btn.getAttribute('data-filter');

                    schoolRows.forEach(row => {
                        if (filter === 'all' || row.getAttribute('data-type') === filter) {
                            row.style.display = 'table-row';
                        } else {
                            row.style.display = 'none';
                        }
                    });
                });
            });

            // Directory Sort Logic
            const sortHeaders = document.querySelectorAll('.sort-header');
            const tbody = document.querySelector('#school-table tbody');

            sortHeaders.forEach(header => {
                header.addEventListener('click', () => {
                    const sortKey = header.getAttribute('data-sort');
                    const isAsc = header.classList.contains('asc');

                    sortHeaders.forEach(h => h.classList.remove('asc', 'desc'));
                    header.classList.add(isAsc ? 'desc' : 'asc');

                    const rows = Array.from(schoolRows);
                    rows.sort((a, b) => {
                        let valA, valB;

                        if (sortKey === 'name') {
                            valA = a.cells[1].childNodes[0].textContent.trim();
                            valB = b.cells[1].childNodes[0].textContent.trim();
                            return isAsc ? valB.localeCompare(valA, 'ja') : valA.localeCompare(valB, 'ja');
                        } else if (sortKey === 'id') {
                            valA = parseInt(a.cells[0].textContent.replace(/[^0-9]/g, '')) || 0;
                            valB = parseInt(b.cells[0].textContent.replace(/[^0-9]/g, '')) || 0;
                            return isAsc ? valA - valB : valB - valA;
                        } else if (sortKey === 'posts') {
                            valA = parseInt(a.cells[5].textContent.replace(/[^0-9]/g, '')) || 0;
                            valB = parseInt(b.cells[5].textContent.replace(/[^0-9]/g, '')) || 0;
                            return isAsc ? valA - valB : valB - valA;
                        } else {
                            valA = parseInt(a.getAttribute('data-followers') || 0);
                            valB = parseInt(b.getAttribute('data-followers') || 0);
                            return isAsc ? valA - valB : valB - valA;
                        }
                    });

                    rows.forEach(row => tbody.appendChild(row));
                });
            });
        });

document.addEventListener('DOMContentLoaded', () => {
            let mapInstance = null;
            let currentMarkers = [];
            let currentCircles = [];
            let schoolCoords = {};
            let currentFilterTypes = new Set(['府立', '市立', 'その他']);
            let currentTargetInfo = null; // { name, lookupName, coords }
            let mapResizeTimeout = null;

            // Load coordinates JSON (embedded to fix local CORS)
            // station: 最寄駅情報
            const data = {
                // 国立・附属
                "京都教育大学附属高等学校": { "lat": 34.9502, "lng": 135.7649, "station": "六地蔵駅（近鉄・地下鉄）" },
                // 府立（京都市内・北部）
                "京都府立清明高等学校": { "lat": 35.0410, "lng": 135.7551, "station": "北大路駅（地下鉄烏丸線）" },
                "京都市立紫野高等学校": { "lat": 35.0446, "lng": 135.7403, "station": "北大路駅（地下鉄烏丸線）" },
                "京都府立鴨沂高等学校": { "lat": 35.0209, "lng": 135.7679, "station": "出町柳駅（京阪・叡電）" },
                "京都府立北稜高等学校": { "lat": 35.0700, "lng": 135.7726, "station": "国際会館駅（地下鉄烏丸線）" },
                "京都府立洛北高等学校": { "lat": 35.0475, "lng": 135.7720, "station": "北大路駅（地下鉄烏丸線）" },
                "京都府立朱雀高等学校": { "lat": 35.0140, "lng": 135.7446, "station": "五条駅（地下鉄烏丸線）" },
                "京都市立堀川高等学校": { "lat": 35.0056, "lng": 135.7526, "station": "二条城前駅（地下鉄東西線）" },
                "京都市立京都堀川音楽高等学校": { "lat": 35.0120, "lng": 135.7420, "station": "二条城前駅（地下鉄東西線）" },
                "京都府立鳥羽高等学校": { "lat": 34.9780, "lng": 135.7446, "station": "竹田駅（地下鉄烏丸線・近鉄）" },
                "京都府立洛東高等学校": { "lat": 34.9966, "lng": 135.8167, "station": "山科駅（JR・地下鉄）" },
                "京都市立日吉ヶ丘高等学校": { "lat": 34.9787, "lng": 135.7764, "station": "東山駅（地下鉄東西線）" },
                "京都市立美術工芸高等学校": { "lat": 34.9867, "lng": 135.7667, "station": "清水五条駅（京阪）" },
                "京都府立嵯峨野高等学校": { "lat": 35.0202, "lng": 135.7037, "station": "花園駅（JR山陰本線）" },
                "京都府立北嵯峨高等学校": { "lat": 35.0254, "lng": 135.6804, "station": "嵯峨嵐山駅（JR山陰本線）" },
                "京都府立桂高等学校": { "lat": 34.9723, "lng": 135.7047, "station": "桂駅（阪急京都線）" },
                "京都府立洛西高等学校": { "lat": 34.9626, "lng": 135.6673, "station": "東向日駅（阪急京都線）" },
                "京都府立東稜高等学校": { "lat": 34.9552, "lng": 135.8183, "station": "六地蔵駅（JR奈良線）" },
                "京都府立洛水高等学校": { "lat": 34.9245, "lng": 135.7337, "station": "桂川駅（JR東海道本線）" },
                "京都市立開建高等学校": { "lat": 34.9677, "lng": 135.7335, "station": "桂川駅（JR東海道本線）" },
                "京都市立西京高等学校": { "lat": 34.9321, "lng": 135.7792, "station": "桂駅（阪急京都線）" },
                "京都市立京都工学院高等学校": { "lat": 34.9393, "lng": 135.7630, "station": "近鉄向島駅（近鉄京都線）" },
                "京都市立京都奏和高等学校": { "lat": 34.9694, "lng": 135.7662, "station": "近鉄向島駅（近鉄京都線）" },
                // 府立（南部）
                "京都府立山城高等学校": { "lat": 35.0229, "lng": 135.7262, "station": "花園駅（JR山陰本線）" },
                "京都府立桃山高等学校": { "lat": 34.9368, "lng": 135.7704, "station": "桃山御陵前駅（近鉄）" },
                "京都府立城南菱創高等学校": { "lat": 34.8921, "lng": 135.7742, "station": "竹田駅（地下鉄烏丸線・近鉄）" },
                "京都府立東宇治高等学校": { "lat": 34.9252, "lng": 135.8098, "station": "黄檗駅（JR奈良線・京阪）" },
                "京都府立莵道高等学校": { "lat": 34.8813, "lng": 135.7972, "station": "三室戸駅（京阪宇治線）" },
                "京都府立城陽高等学校": { "lat": 34.8524, "lng": 135.7891, "station": "城陽駅（JR奈良線）" },
                "京都府立西城陽高等学校": { "lat": 34.8430, "lng": 135.7660, "station": "近鉄富野荘駅（近鉄京都線）" },
                "京都府立京都八幡高等学校": { "lat": 34.8597, "lng": 135.7014, "station": "八幡市駅（京阪本線）" },
                "京都府立久御山高等学校": { "lat": 34.8813, "lng": 135.7562, "station": "近鉄向島駅（近鉄京都線）" },
                "京都府立田辺高等学校": { "lat": 34.8212, "lng": 135.7775, "station": "近鉄興戸駅（近鉄京都線）" },
                "京都府立木津高等学校": { "lat": 34.7387, "lng": 135.8313, "station": "木津駅（JR奈良線・学研都市線）" },
                "京都府立南陽高等学校・附属中学校": { "lat": 34.7765, "lng": 135.8279, "station": "加茂駅（JR大和路線）" },
                "京都府立京都すばる高等学校": { "lat": 34.9130, "lng": 135.7700, "station": "近鉄伊勢田駅（近鉄京都線）" },
                "京都府立向陽高等学校": { "lat": 34.9598, "lng": 135.6883, "station": "東向日駅（阪急京都線）" },
                "京都府立清新高等学校": { "lat": 34.8785, "lng": 135.7974, "station": "黄檗駅（JR奈良線・京阪）" },
                // 府立（乙訓）
                "京都府立乙訓高等学校": { "lat": 34.9188, "lng": 135.6936, "station": "長岡京駅（JR東海道本線）" },
                "京都府立西乙訓高等学校": { "lat": 34.9135, "lng": 135.6788, "station": "長岡京駅（JR東海道本線）" },
                // 府立（亀岡・丹波）
                "京都府立亀岡高等学校": { "lat": 35.0110, "lng": 135.5822, "station": "亀岡駅（JR山陰本線）" },
                "京都府立南丹高等学校": { "lat": 35.0544, "lng": 135.5565, "station": "園部駅（JR山陰本線）" },
                "京都府立園部高等学校・附属中学校": { "lat": 35.0559, "lng": 135.4605, "station": "園部駅（JR山陰本線）" },
                "京都府立農芸高等学校": { "lat": 35.0558, "lng": 135.4550, "station": "胡麻駅（JR山陰本線）" },
                "京都府立須知高等学校": { "lat": 35.1732, "lng": 135.4155, "station": "和知駅（JR山陰本線）" },
                "京都府立北桑田高等学校": { "lat": 35.1964, "lng": 135.6324, "station": "山家駅（JR山陰本線）" },
                // 府立（中丹・北部）
                "京都府立綾部高等学校": { "lat": 35.3009, "lng": 135.2377, "station": "綾部駅（JR山陰本線）" },
                "京都府立福知山高等学校・附属中学校": { "lat": 35.2939, "lng": 135.1268, "station": "福知山駅（JR山陰本線）" },
                "京都府立工業高等学校": { "lat": 35.2973, "lng": 135.1768, "station": "福知山駅（JR山陰本線）" },
                "京都府立大江高等学校": { "lat": 35.3938, "lng": 135.1575, "station": "大江駅（京都丹後鉄道）" },
                // 府立（舞鶴・丹後）
                "京都府立東舞鶴高等学校": { "lat": 35.4839, "lng": 135.4151, "station": "東舞鶴駅（JR舞鶴線）" },
                "京都府立西舞鶴高等学校": { "lat": 35.4386, "lng": 135.3278, "station": "西舞鶴駅（JR・京都丹後鉄道）" },
                "京都府立海洋高等学校": { "lat": 35.5509, "lng": 135.2355, "station": "丹後由良駅（京都丹後鉄道）" },
                "京都府立峰山高等学校": { "lat": 35.6249, "lng": 135.0546, "station": "峰山駅（京都丹後鉄道）" },
                "京都府立宮津天橋高等学校": { "lat": 35.5293, "lng": 135.1897, "station": "宮津駅（京都丹後鉄道）" },
                "京都府立丹後緑風高等学校": { "lat": 35.6340, "lng": 135.0480, "station": "網野駅（京都丹後鉄道）" },
                // 私立・その他
                "一燈園高等学校": { "lat": 34.9918, "lng": 135.8115, "station": "六地蔵駅（JR奈良線）" },
                "大谷高等学校": { "lat": 34.9844, "lng": 135.7720, "station": "七条駅（京阪本線）" },
                "華頂女子高等学校": { "lat": 35.0071, "lng": 135.7808, "station": "東山駅（地下鉄東西線）" },
                "京都外大西高等学校": { "lat": 34.9340, "lng": 135.7140, "station": "東向日駅（阪急京都線）" },
                "京都光華高等学校": { "lat": 34.9827, "lng": 135.7467, "station": "西院駅（阪急・京福）" },
                "京都国際高等学校": { "lat": 34.9780, "lng": 135.7446, "station": "竹田駅（地下鉄烏丸線・近鉄）" },
                "京都産業大学附属高等学校": { "lat": 35.0620, "lng": 135.7180, "station": "国際会館駅（地下鉄烏丸線）" },
                "京都女子高等学校": { "lat": 34.9960, "lng": 135.7780, "station": "七条駅（京阪本線）" },
                "京都精華学園高等学校": { "lat": 34.9911, "lng": 135.7482, "station": "竹田駅（地下鉄烏丸線・近鉄）" },
                "京都成章高等学校": { "lat": 34.9530, "lng": 135.7050, "station": "桂駅（阪急京都線）" },
                "京都聖母学院高等学校": { "lat": 35.0220, "lng": 135.7780, "station": "蹴上駅（地下鉄東西線）" },
                "京都橘高等学校": { "lat": 34.9694, "lng": 135.7662, "station": "六地蔵駅（JR奈良線）" },
                "京都つくば開成高等学校": { "lat": 34.9897, "lng": 135.7554, "station": "五条駅（地下鉄烏丸線）" },
                "京都文教高等学校": { "lat": 34.8870, "lng": 135.8000, "station": "近鉄小倉駅（近鉄京都線）" },
                "京都美山高等学校": { "lat": 35.3750, "lng": 135.6710, "station": "日吉駅（JR山陰本線）" },
                "京都明徳高等学校": { "lat": 34.9060, "lng": 135.7760, "station": "近鉄大久保駅（近鉄京都線）" },
                "京都両洋高等学校": { "lat": 35.0090, "lng": 135.7430, "station": "二条駅（地下鉄東西線・JR）" },
                "同志社高等学校": { "lat": 35.0027, "lng": 135.7666, "station": "今出川駅（地下鉄烏丸線）" },
                "同志社女子高等学校": { "lat": 35.0320, "lng": 135.7810, "station": "神宮丸太町駅（京阪）" },
                "花園高等学校": { "lat": 35.0217, "lng": 135.7227, "station": "花園駅（JR山陰本線）" },
                "東山高等学校": { "lat": 34.9900, "lng": 135.7810, "station": "七条駅（京阪本線）" },
                "平安女学院高等学校": { "lat": 35.0196, "lng": 135.7585, "station": "今出川駅（地下鉄烏丸線）" },
                "洛星高等学校": { "lat": 35.0380, "lng": 135.7180, "station": "北野白梅町駅（京福電鉄）" },
                "洛南高等学校": { "lat": 34.9827, "lng": 135.7467, "station": "東寺駅（近鉄京都線）" },
                "洛陽総合高等学校": { "lat": 35.0116, "lng": 135.7369, "station": "二条駅（地下鉄東西線・JR）" },
                "龍谷大学付属平安高等学校": { "lat": 34.9815, "lng": 135.7480, "station": "東寺駅（近鉄京都線）" },
                "京都芸術高等学校": { "lat": 34.9133, "lng": 135.8042, "station": "近鉄大久保駅（近鉄京都線）" },
                "京都翔英高等学校": { "lat": 34.8874, "lng": 135.8021, "station": "近鉄大久保駅（近鉄京都線）" },
                "立命館宇治高等学校": { "lat": 34.8950, "lng": 135.8010, "station": "近鉄大久保駅（近鉄京都線）" },
                "京都西山高等学校": { "lat": 34.9100, "lng": 135.6740, "station": "長岡天神駅（阪急京都線）" },
                "立命館高等学校": { "lat": 35.0160, "lng": 135.7120, "station": "太秦天神川駅（地下鉄東西線）" },
                "同志社国際高等学校": { "lat": 34.8480, "lng": 135.7120, "station": "近鉄三山木駅（近鉄京都線）" },
                "京都廣学館高等学校": { "lat": 34.9897, "lng": 135.7554, "station": "五条駅（地下鉄烏丸線）" },
                "京都聖カタリナ高等学校": { "lat": 34.7300, "lng": 135.7200, "station": "山田川駅（近鉄京都線）" },
                "京都共栄学園高等学校": { "lat": 35.2900, "lng": 135.1270, "station": "福知山駅（JR山陰本線）" },
                "福知山成美高等学校": { "lat": 35.2980, "lng": 135.1080, "station": "福知山駅（JR山陰本線）" },
                "福知山淑徳高等学校": { "lat": 35.2900, "lng": 135.1008, "station": "福知山駅（JR山陰本線）" },
                "日星高等学校": { "lat": 35.4680, "lng": 135.3990, "station": "東舞鶴駅（JR舞鶴線）" },
                "京都暁星高等学校": { "lat": 35.5502, "lng": 135.2122, "station": "宮津駅（京都丹後鉄道）" },
                "ノートルダム女学院高等学校": { "lat": 35.0232, "lng": 135.7972, "station": "出町柳駅（京阪・叡電）" }
            };
            schoolCoords = Object.keys(data).reduce((acc, key) => {
                acc[key.replace(/\s+/g, '')] = data[key];
                return acc;
            }, {});
            console.log("Coordinates loaded for", Object.keys(schoolCoords).length, "schools");
            initMapButtons();

            // Distance calculation
            function getDistanceFromLatLonInKm(lat1, lon1, lat2, lon2) {
                var R = 6371; // Radius of the earth in km
                var dLat = deg2rad(lat2 - lat1);
                var dLon = deg2rad(lon2 - lon1);
                var a =
                    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                    Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
                    Math.sin(dLon / 2) * Math.sin(dLon / 2);
                var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
                var d = R * c; // Distance in km
                return d;
            }

            function deg2rad(deg) {
                return deg * (Math.PI / 180)
            }

            function initMapButtons() {
                // Add map button to each school row in directory
                const rows = document.querySelectorAll('#school-table tbody tr');
                rows.forEach(row => {
                    const schoolNameCell = row.cells[1];
                    // Retrieve only the original school name text, avoiding elements added later
                    const originalName = Array.from(schoolNameCell.childNodes)
                        .filter(n => n.nodeType === Node.TEXT_NODE)
                        .map(n => n.textContent)
                        .join('')
                        .trim();

                    // Create button inside the cell
                    const div = document.createElement('div');
                    div.className = 'mt-2 block';
                    div.innerHTML = `
                        <button class="open-map-btn text-[10px] md:text-xs px-3 py-1.5 bg-slate-800 hover:bg-blue-600/80 text-blue-300 hover:text-white border border-slate-700 hover:border-blue-500 rounded-full flex items-center gap-1.5 transition-all duration-300 w-max whitespace-nowrap">
                            <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                            周辺の競合校を見る
                        </button>
                    `;
                    schoolNameCell.appendChild(div);

                    const btn = div.querySelector('.open-map-btn');
                    btn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        openMapModal(originalName);
                    });
                });
            }

            function openMapModal(targetSchoolName) {
                const modal = document.getElementById('map-modal');
                const modalContent = document.getElementById('map-modal-content');
                const titleSpan = document.getElementById('map-school-name');

                // Clean name for lookup
                const lookupName = targetSchoolName.replace(/\s+/g, '');
                const targetCoords = schoolCoords[lookupName] || schoolCoords[lookupName.replace('高等学校', '高校')];

                if (!targetCoords) {
                    alert(`${targetSchoolName} の位置データが見つかりませんでした。`);
                    return;
                }

                titleSpan.textContent = targetSchoolName;

                // Show modal
                modal.classList.remove('pointer-events-none');
                // Small delay for CSS transition
                setTimeout(() => {
                    modal.classList.remove('opacity-0');
                    modalContent.classList.remove('scale-95');
                }, 10);

                // Initialize or update map
                if (!mapInstance) {
                    // Dark theme map tiles (CartoDB Dark Matter)
                    mapInstance = L.map('school-map').setView([targetCoords.lat, targetCoords.lng], 13);
                    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
                        subdomains: 'abcd',
                        maxZoom: 19
                    }).addTo(mapInstance);
                    // 行政界オーバーレイ（都道府県・市区町村境）
                    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        opacity: 0.18, maxZoom: 19, attribution: ''
                    }).addTo(mapInstance);
                    // 通学圏ゾーン境界
                    addTsuugakuken();
                } else {
                    mapInstance.setView([targetCoords.lat, targetCoords.lng], 13);
                }

                // Invalidate size to ensure it renders correctly after modal open
                if (mapResizeTimeout) clearTimeout(mapResizeTimeout);
                mapResizeTimeout = setTimeout(() => {
                    mapInstance.invalidateSize();
                }, 300);

                // Clear previous markers and circles
                currentMarkers.forEach(m => mapInstance.removeLayer(m));
                currentMarkers = [];
                currentCircles.forEach(c => mapInstance.removeLayer(c));
                currentCircles = [];

                // Define target icon
                const targetIcon = L.divIcon({
                    className: 'custom-div-icon',
                    html: `<div class="w-5 h-5 bg-blue-500 rounded-full border-2 border-white shadow-[0_0_15px_rgba(59,130,246,0.8)] animate-pulse"></div>`,
                    iconSize: [20, 20],
                    iconAnchor: [10, 10]
                });

                // Add 5km circle (outline only, no fill)
                currentCircles.push(L.circle([targetCoords.lat, targetCoords.lng], {
                    color: '#f43f5e', fillOpacity: 0, weight: 1.5, dashArray: '6, 4'
                }).setRadius(5000).addTo(mapInstance));

                // Add 10km circle (outline only, no fill)
                currentCircles.push(L.circle([targetCoords.lat, targetCoords.lng], {
                    color: '#f97316', fillOpacity: 0, weight: 1.5, dashArray: '6, 4'
                }).setRadius(10000).addTo(mapInstance));

                // Save target info for re-render on filter change
                currentTargetInfo = { name: targetSchoolName, lookupName, coords: targetCoords };

                // Plot target school
                const shortTargetName = targetSchoolName.replace(/京都府立|京都市立|京都府/, '');
                const station0 = (schoolCoords[lookupName] || {}).station || '';
                const tMarker = L.marker([targetCoords.lat, targetCoords.lng], { icon: targetIcon })
                    .addTo(mapInstance)
                    .bindTooltip(shortTargetName, { permanent: true, direction: 'top', className: 'map-label target-label', offset: [0, -10] })
                    .bindPopup(`<div class="text-center font-bold text-blue-400 mb-1">選択対象</div><div class="text-white text-md border-b border-slate-600 pb-1">${targetSchoolName}</div>${station0 ? `<div class="text-xs text-slate-400 mt-1">🚉 ${station0}</div>` : ''}<div class="text-xs text-slate-400 mt-1">商圏中心点</div>`);
                currentMarkers.push(tMarker);

                renderCompetitors(targetCoords, lookupName);
            }

            function getSchoolType(name) {
                if (name.includes('府立')) return '府立';
                if (name.includes('市立')) return '市立';
                return 'その他';
            }

            function renderCompetitors(targetCoords, lookupName) {
                // Remove existing competitor markers (keep index 0 = target)
                currentMarkers.slice(1).forEach(m => mapInstance.removeLayer(m));
                currentMarkers = currentMarkers.slice(0, 1);

                Object.keys(schoolCoords).forEach(key => {
                    if (key === lookupName) return;

                    const schoolType = getSchoolType(key);
                    if (!currentFilterTypes.has(schoolType)) return;

                    const coords = schoolCoords[key];
                    const dist = getDistanceFromLatLonInKm(targetCoords.lat, targetCoords.lng, coords.lat, coords.lng);

                    // Color and size by distance zone
                    let color, shadow, size;
                    if (dist <= 5.0) {
                        color = '#f43f5e'; shadow = 'rgba(244,63,94,0.7)'; size = 14;
                    } else if (dist <= 10.0) {
                        color = '#f97316'; shadow = 'rgba(249,115,22,0.5)'; size = 12;
                    } else {
                        color = '#64748b'; shadow = 'rgba(100,116,139,0.3)'; size = 10;
                    }

                    const icon = L.divIcon({
                        className: 'custom-div-icon',
                        html: `<div style="width:${size}px;height:${size}px;background:${color};border-radius:50%;border:2px solid white;box-shadow:0 0 8px ${shadow}"></div>`,
                        iconSize: [size, size],
                        iconAnchor: [size / 2, size / 2]
                    });

                    const shortName = key.replace(/京都府立|京都市立|京都府/, '');
                    const station = coords.station || '';
                    const stationHtml = station ? `<div class="text-xs text-slate-400 mt-1">🚉 ${station}</div>` : '';
                    const zoneLabel = dist <= 5.0 ? '5km圏内' : dist <= 10.0 ? '10km圏内' : `${dist.toFixed(0)}km`;
                    const zoneColor = dist <= 5.0 ? 'text-rose-400' : dist <= 10.0 ? 'text-orange-400' : 'text-slate-400';

                    // Permanent tooltip for ≤10km, hover-only for >10km
                    const tooltipPermanent = true;
                    const m = L.marker([coords.lat, coords.lng], { icon })
                        .addTo(mapInstance)
                        .bindTooltip(shortName, { permanent: tooltipPermanent, direction: 'top', className: 'map-label', offset: [0, -(size / 2) - 4] })
                        .bindPopup(`<div class="text-center ${zoneColor} text-xs font-bold mb-1">${zoneLabel}</div><div class="text-white font-bold">${key}</div><div class="text-xs text-slate-400 mt-1">直線距離: ${dist.toFixed(1)} km</div>${stationHtml}`);
                    currentMarkers.push(m);
                });
            }

            // Filter button toggle
            document.querySelectorAll('.map-filter-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const type = btn.dataset.type;
                    if (currentFilterTypes.has(type)) {
                        currentFilterTypes.delete(type);
                        btn.classList.remove('map-filter-active');
                    } else {
                        currentFilterTypes.add(type);
                        btn.classList.add('map-filter-active');
                    }
                    if (currentTargetInfo) {
                        renderCompetitors(currentTargetInfo.coords, currentTargetInfo.lookupName);
                    }
                });
            });

            function closeMapModal() {
                if (mapResizeTimeout) { clearTimeout(mapResizeTimeout); mapResizeTimeout = null; }
                const modal = document.getElementById('map-modal');
                const modalContent = document.getElementById('map-modal-content');
                modal.classList.add('opacity-0');
                modalContent.classList.add('scale-95');
                modal.classList.add('pointer-events-none');
            }

            function addTsuugakuken() {
                // 京都府公立高校 通学圏（地域）境界（近似ポリゴン）
                // 参考：京都府公立高校所在地図（令和5年度版）
                const zones = [
                    {
                        name: '京都市・乙訓通学圏',
                        // 京都市全域（京都東北小中学校区を除く）＋向日市・長岡京市・大山崎町
                        // ＋八幡市（八幡長町・八幡橋ノ口・川口高原）＋久御山町（大橋辺）
                        coords: [
                            [35.148, 135.732], // 北（鞍馬・貴船方面）
                            [35.140, 135.793], // 北東（左京区）
                            [35.088, 135.868], // 東（山科区東端）
                            [34.999, 135.858], // 南東（伏見区南東）
                            [34.940, 135.827], // 南（伏見区南端）
                            [34.925, 135.790], // 南（城南菱創より北 / 山城境界）
                            [34.913, 135.748], // 南西（山城との境界点）
                            [34.866, 135.726], // 南（八幡境界）
                            [34.860, 135.706], // 南西（八幡 / 久御山境界）
                            [34.850, 135.688], // 南（大山崎町南端 / 大阪府境）
                            [34.843, 135.664], // 西南（大阪府境）
                            [34.858, 135.644], // 西（西京区西端）
                            [34.904, 135.639], // 西（右京区南西）
                            [34.944, 135.667], // 西南（右京区 / 西京区境）
                            [34.970, 135.629], // 西（右京区西端）
                            [35.014, 135.629], // 北西（右京区北西）
                            [35.067, 135.644], // 北（北区西）
                            [35.090, 135.636], // 北西（北区北西端 / 京北境界）
                            [35.116, 135.714]  // 北（北区北端）
                        ],
                        color: '#60a5fa',
                        labelPos: [35.020, 135.748]
                    },
                    {
                        name: '山城通学圏',
                        // 宇治市・城陽市・八幡市（大部分）・京田辺市・木津川市
                        // 久御山町（大部分）・井手町・宇治田原町・笠置町・和束町・精華町・南山城村
                        coords: [
                            [34.913, 135.748], // 北西（城南菱創を含む / 伏見区境）
                            [34.925, 135.790], // 北中（城南菱創の北側）
                            [34.940, 135.827], // 北（伏見区南端）
                            [34.999, 135.858], // 北（京都市南東端）
                            [35.000, 135.906], // 北東
                            [34.960, 135.916], // 東（宇治田原 / 滋賀境）
                            [34.878, 135.916], // 東（木津川東端 / 奈良境）
                            [34.798, 135.902], // 南東（南山城村南東）
                            [34.752, 135.872], // 南（奈良県境）
                            [34.720, 135.822], // 南（奈良県境）
                            [34.742, 135.748], // 南西（奈良 / 大阪境）
                            [34.782, 135.706], // 西（大阪府境 / 八幡市南）
                            [34.812, 135.686], // 西（大阪府境 / 八幡北）
                            [34.850, 135.688], // 北西
                            [34.860, 135.695], // 北（京都八幡を含むため西に拡張）
                            [34.866, 135.726]  // 北
                        ],
                        color: '#f59e0b',
                        labelPos: [34.850, 135.810]
                    },
                    {
                        name: '口丹通学圏',
                        // 亀岡市・南丹市・京丹波町＋京都市（京都東北小中学校区＝京北地区）
                        // ※ 亀岡市は西山トンネル西側、京都市中心部とは別ゾーン
                        coords: [
                            [35.090, 135.636], // 東南（北区北西 / 京北境界）
                            [35.116, 135.714], // 東南（北区北端）
                            [35.148, 135.732], // 東（左京区北 / 京北境界）
                            [35.240, 135.670], // 東（京北地区）
                            [35.380, 135.700], // 北東（京丹波北東）
                            [35.460, 135.600], // 北（京丹波北）
                            [35.380, 135.410], // 北西（京丹波 / 兵庫境）
                            [35.200, 135.368], // 西（南丹市西）
                            [35.048, 135.430], // 南西（南丹市南）
                            [34.986, 135.494], // 南（亀岡市南端 / 大阪境）
                            [34.944, 135.570], // 南東（亀岡 / 京都市境）
                            [34.944, 135.667], // 東（京都市西南端）
                            [34.970, 135.629], // 東（右京区西）
                            [35.014, 135.629], // 東（右京区北西）
                            [35.067, 135.644]  // 東（北区西）
                        ],
                        color: '#a78bfa',
                        labelPos: [35.100, 135.510]
                    }
                ];

                zones.forEach(zone => {
                    L.polygon(zone.coords, {
                        color: zone.color, weight: 2, dashArray: '8, 5',
                        fillOpacity: 0.05, fillColor: zone.color, interactive: false
                    }).addTo(mapInstance);
                    L.marker(zone.labelPos, {
                        icon: L.divIcon({
                            className: '',
                            html: `<div style="color:${zone.color};font-size:10px;font-weight:bold;white-space:nowrap;opacity:0.85;text-shadow:0 0 4px #000,0 0 8px #000;">${zone.name}</div>`,
                            iconAnchor: [40, 6]
                        }),
                        interactive: false
                    }).addTo(mapInstance);
                });
            }

            document.getElementById('close-map').addEventListener('click', closeMapModal);

            // Close on backdrop click
            document.getElementById('map-modal').addEventListener('click', (e) => {
                if (e.target.id === 'map-modal') closeMapModal();
            });

            // Close on Escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && !document.getElementById('map-modal').classList.contains('opacity-0')) {
                    closeMapModal();
                }
            });
        });

(function() {
            var toggle = document.getElementById('theme-toggle');
            var icon = document.getElementById('theme-icon');
            var label = document.getElementById('theme-label');

            function updateUI() {
                var isLight = document.documentElement.classList.contains('light-mode');
                icon.textContent = isLight ? '🌙' : '☀️';
                label.textContent = isLight ? 'ダークモード' : 'ライトモード';
            }

            updateUI();

            toggle.addEventListener('click', function() {
                document.documentElement.classList.toggle('light-mode');
                var isLight = document.documentElement.classList.contains('light-mode');
                localStorage.setItem('theme', isLight ? 'light' : 'dark');
                updateUI();
            });
        })();

(function () {
            const EXPECTED_HASH = '154103b7962882f8b48e07bcd71e1c002f021df609735693841aa45ad1c8583f';
            const STORAGE_KEY = 'tobabuzz_auth';
            const overlay = document.getElementById('auth-overlay');

            // 認証済みチェック
            if (localStorage.getItem(STORAGE_KEY) === EXPECTED_HASH) {
                return; // すでに認証済み → 何もしない
            }

            // 未認証 → オーバーレイ表示
            overlay.style.display = 'flex';
            document.getElementById('auth-input').focus();

            async function sha256(message) {
                const msgBuffer = new TextEncoder().encode(message);
                const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
                return Array.from(new Uint8Array(hashBuffer))
                    .map(b => b.toString(16).padStart(2, '0')).join('');
            }

            async function tryAuth() {
                const input = document.getElementById('auth-input').value;
                const errorEl = document.getElementById('auth-error');
                if (!input) { errorEl.textContent = 'パスワードを入力してください'; return; }
                const hash = await sha256(input);
                if (hash === EXPECTED_HASH) {
                    localStorage.setItem(STORAGE_KEY, EXPECTED_HASH);
                    overlay.style.opacity = '0';
                    overlay.style.transition = 'opacity 0.4s ease';
                    setTimeout(() => { overlay.style.display = 'none'; }, 400);
                } else {
                    errorEl.textContent = 'パスワードが違います';
                    document.getElementById('auth-input').value = '';
                    document.getElementById('auth-input').focus();
                }
            }

            document.getElementById('auth-btn').addEventListener('click', tryAuth);
            document.getElementById('auth-input').addEventListener('keydown', function (e) {
                if (e.key === 'Enter') tryAuth();
            });
        })();


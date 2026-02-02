import streamlit as st
import streamlit.components.v1 as components

# Konfigurasi Halaman Streamlit agar tampilan penuh (wide)
st.set_page_config(
    page_title="Dashboard Monitoring Sekolah",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Seluruh kode UI (HTML, CSS, JS) disimpan dalam variabel html_code
html_code = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Monitoring Pemasangan Sekolah</title>
    <!-- Framework CSS Tailwind untuk desain modern -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Library Ikon Lucide -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        body { 
            font-family: 'Inter', sans-serif; 
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }
        .animate-spin-slow { animation: spin 2s linear infinite; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        
        /* Kustomisasi Scrollbar agar lebih rapi */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #f1f1f1; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
    </style>
</head>
<body class="bg-slate-50 text-slate-900">

    <div id="app" class="p-4 md:p-8">
        <!-- Header Dashboard -->
        <div class="max-w-6xl mx-auto mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <h1 class="text-3xl font-bold text-slate-800 flex items-center gap-3">
                    <i data-lucide="layout-dashboard" class="text-blue-600 w-8 h-8"></i>
                    Monitoring Pemasangan Sekolah
                </h1>
                <p class="text-slate-500 mt-1 italic text-sm md:text-base">Laporan real-time status instalasi berdasarkan data Spreadsheet.</p>
            </div>
            <button id="refreshBtn" class="flex items-center justify-center gap-2 bg-white border border-slate-200 px-5 py-2.5 rounded-xl hover:bg-slate-50 transition-all shadow-sm font-semibold text-slate-700 active:scale-95">
                <i data-lucide="refresh-cw" id="refreshIcon" class="w-5 h-5"></i>
                Refresh Data
            </button>
        </div>

        <!-- Ringkasan Statistik (Stat Cards) -->
        <div class="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <!-- Sekolah Terpasang (Hijau) -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-emerald-100 flex items-center gap-6">
                <div class="bg-emerald-100 p-4 rounded-2xl text-emerald-600">
                    <i data-lucide="check-circle" class="w-10 h-10"></i>
                </div>
                <div>
                    <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">Sekolah Terpasang</p>
                    <h2 id="countInstalled" class="text-4xl font-black text-emerald-600">0</h2>
                </div>
            </div>

            <!-- Sekolah Bermasalah (Merah) -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-rose-100 flex items-center gap-6">
                <div class="bg-rose-100 p-4 rounded-2xl text-rose-600">
                    <i data-lucide="alert-circle" class="w-10 h-10"></i>
                </div>
                <div>
                    <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">Sekolah Bermasalah</p>
                    <h2 id="countTrouble" class="text-4xl font-black text-rose-600">0</h2>
                </div>
            </div>
        </div>

        <!-- Tabel Detail Trouble -->
        <div class="max-w-6xl mx-auto bg-white rounded-2xl shadow-md border border-slate-200 overflow-hidden">
            <div class="p-6 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <h3 class="text-xl font-bold flex items-center gap-2 text-slate-800">
                    <i data-lucide="file-text" class="text-rose-500"></i>
                    Daftar Detail Kerusakan (Trouble)
                </h3>
                <div class="relative">
                    <i data-lucide="search" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4"></i>
                    <input 
                        type="text" 
                        id="searchInput"
                        placeholder="Cari NPSN atau Nama..." 
                        class="pl-10 pr-4 py-2 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 w-full md:w-72 text-sm transition-all"
                    >
                </div>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead class="bg-slate-50 text-slate-500">
                        <tr>
                            <th class="px-6 py-4 font-semibold uppercase text-xs tracking-wider">NPSN</th>
                            <th class="px-6 py-4 font-semibold uppercase text-xs tracking-wider">Nama Sekolah</th>
                            <th class="px-6 py-4 font-semibold uppercase text-xs tracking-wider">Status</th>
                            <th class="px-6 py-4 font-semibold uppercase text-xs tracking-wider text-rose-600">Reason / Alasan</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody" class="divide-y divide-slate-100">
                        <!-- Konten akan dimuat oleh JavaScript -->
                    </tbody>
                </table>
            </div>
        </div>

        <div id="demoNotice" class="hidden max-w-6xl mx-auto mt-6 p-4 bg-amber-50 border border-amber-200 rounded-xl text-amber-800 text-xs md:text-sm">
            <strong>Catatan:</strong> Menampilkan data demo. Pastikan URL CSV diisi di variabel SPREADSHEET_CSV_URL.
        </div>
    </div>

    <script>
        // --- KONFIGURASI SPREADSHEET ---
        // Ganti string kosong di bawah ini dengan URL CSV Google Sheets Anda
        // Format: Publish to Web -> Comma-separated values (.csv)
        const SPREADSHEET_CSV_URL = ""; 

        let masterData = [];

        function initIcons() {
            lucide.createIcons();
        }

        const dummyData = [
            { npsn: '1001', nama: 'SDN Contoh 01', status_warna: 'hijau', reason: '-' },
            { npsn: '1002', nama: 'SDN Contoh 02', status_warna: 'merah', reason: 'Kabel terputus proyek jalan' },
            { npsn: '1003', nama: 'SMPN Contoh 05', status_warna: 'hijau', reason: '-' },
            { npsn: '1004', nama: 'SMKN Contoh 01', status_warna: 'merah', reason: 'Antena tersambar petir' }
        ];

        async function fetchData() {
            const btn = document.getElementById('refreshBtn');
            const icon = document.getElementById('refreshIcon');
            btn.disabled = true;
            icon.classList.add('animate-spin');

            try {
                if (!SPREADSHEET_CSV_URL) {
                    masterData = dummyData;
                    document.getElementById('demoNotice').classList.remove('hidden');
                } else {
                    const response = await fetch(SPREADSHEET_CSV_URL);
                    const csvText = await response.text();
                    
                    // Parsing baris CSV, memisahkan per baris dan kolom
                    const rows = csvText.split('\\n').slice(1);
                    masterData = rows.map(row => {
                        const cols = row.match(/(".*?"|[^",\\s]+)(?=\\s*,|\\s*$)/g);
                        if (!cols) return null;
                        return {
                            npsn: cols[0]?.replace(/"/g, '').trim(),
                            nama: cols[1]?.replace(/"/g, '').trim(),
                            status_warna: cols[2]?.replace(/"/g, '').toLowerCase().trim(),
                            reason: cols[3]?.replace(/"/g, '').trim() || '-'
                        };
                    }).filter(item => item && item.npsn);
                    
                    document.getElementById('demoNotice').classList.add('hidden');
                }
                renderDashboard();
            } catch (err) {
                console.error("Fetch Error:", err);
            } finally {
                btn.disabled = false;
                icon.classList.remove('animate-spin');
            }
        }

        function renderDashboard() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            
            // Filter data berdasarkan pemicu (hijau = terpasang, merah = trouble)
            const installed = masterData.filter(d => d.status_warna === 'hijau');
            const trouble = masterData.filter(d => d.status_warna === 'merah');

            document.getElementById('countInstalled').innerText = installed.length;
            document.getElementById('countTrouble').innerText = trouble.length;

            const filteredTrouble = trouble.filter(d => 
                d.npsn.toLowerCase().includes(searchTerm) || 
                d.nama.toLowerCase().includes(searchTerm)
            );

            const tableBody = document.getElementById('tableBody');
            tableBody.innerHTML = '';

            if (filteredTrouble.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="4" class="px-6 py-12 text-center text-slate-400 font-medium">Tidak ada data kerusakan ditemukan.</td></tr>`;
            } else {
                filteredTrouble.forEach(item => {
                    tableBody.innerHTML += `
                        <tr class="hover:bg-rose-50/40 transition-colors">
                            <td class="px-6 py-4 font-mono font-bold text-slate-600">\${item.npsn}</td>
                            <td class="px-6 py-4 font-semibold text-slate-800">\${item.nama}</td>
                            <td class="px-6 py-4">
                                <span class="px-3 py-1 bg-rose-100 text-rose-700 rounded-full text-[10px] font-black uppercase tracking-wider">Bermasalah</span>
                            </td>
                            <td class="px-6 py-4 italic text-slate-500">\${item.reason}</td>
                        </tr>`;
                });
            }
        }

        // Listener untuk tombol refresh dan kotak pencarian
        document.getElementById('refreshBtn').addEventListener('click', fetchData);
        document.getElementById('searchInput').addEventListener('input', renderDashboard);

        window.onload = () => {
            initIcons();
            fetchData();
        };
    </script>
</body>
</html>
"""

# Menampilkan HTML ke dalam frame Streamlit
# Tinggi diset 900 agar cukup untuk tabel yang panjang
components.html(html_code, height=1000, scrolling=True)

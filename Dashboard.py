import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Dashboard Monitoring Pemasangan Sekolah",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KONFIGURASI SPREADSHEET ---
# Link ekspor CSV dari Google Sheets Anda
URL_SPREADSHEET = "https://docs.google.com/spreadsheets/d/1cf3listhOUa_7bURBzrnCVMMM_B3h931nW6ZxsaEPvI/export?format=csv"

def get_data():
    try:
        # Menarik data menggunakan Python agar lebih stabil dan bypass CORS
        df = pd.read_csv(URL_SPREADSHEET)
        # Membersihkan nama kolom dari spasi
        df.columns = [c.strip() for c in df.columns]
        return df.to_dict(orient='records')
    except Exception as e:
        return []

# Ambil data terbaru
data_sekolah = get_data()
data_json = json.dumps(data_sekolah)

# Struktur Antarmuka (HTML/CSS/JS)
html_code = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
        .glass-card { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); }
        .animate-pulse-slow { animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
    </style>
</head>
<body class="p-4 md:p-8">

    <div class="max-w-6xl mx-auto">
        <!-- Header Section -->
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
            <div>
                <h1 class="text-3xl font-extrabold text-slate-800 flex items-center gap-3">
                    <div class="p-2 bg-indigo-600 rounded-lg text-white">
                        <i data-lucide="database"></i>
                    </div>
                    Monitoring Berbasis NPSN
                </h1>
                <p class="text-slate-500 mt-1 uppercase text-[10px] font-bold tracking-[0.2em]">Data Terpusat Google Sheets</p>
            </div>
            <div class="flex flex-col items-end">
                <button onclick="window.location.reload()" class="flex items-center gap-2 bg-indigo-600 text-white px-5 py-2.5 rounded-xl hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-100 font-semibold active:scale-95">
                    <i data-lucide="refresh-cw" size="18"></i> Refresh
                </button>
            </div>
        </div>

        <!-- Kartu Statistik -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <!-- Counter Terpasang -->
            <div class="glass-card p-6 rounded-3xl border border-emerald-100 shadow-sm flex items-center gap-6">
                <div class="bg-emerald-500 p-4 rounded-2xl text-white">
                    <i data-lucide="check-circle-2" size="32"></i>
                </div>
                <div>
                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Total Terinstall</p>
                    <h2 id="installedCount" class="text-5xl font-black text-emerald-600 tracking-tighter">0</h2>
                </div>
            </div>

            <!-- Counter Trouble -->
            <div class="glass-card p-6 rounded-3xl border border-rose-100 shadow-sm flex items-center gap-6">
                <div class="bg-rose-500 p-4 rounded-2xl text-white animate-pulse-slow">
                    <i data-lucide="alert-circle" size="32"></i>
                </div>
                <div>
                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Total Trouble</p>
                    <h2 id="troubleCount" class="text-5xl font-black text-rose-600 tracking-tighter">0</h2>
                </div>
            </div>
        </div>

        <!-- Daftar Trouble Berdasarkan Validasi NPSN -->
        <div class="bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden">
            <div class="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/30">
                <h3 class="text-lg font-bold text-slate-800 flex items-center gap-2">
                    <i data-lucide="table-properties" class="text-indigo-500"></i>
                    Rincian Kendala Sekolah
                </h3>
                <span id="timestamp" class="text-[10px] font-mono text-slate-400 uppercase"></span>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left">
                    <thead class="bg-slate-50 text-slate-400 text-[10px] uppercase font-bold tracking-widest">
                        <tr>
                            <th class="px-8 py-5">NPSN (Trigger)</th>
                            <th class="px-8 py-5">Nama Sekolah</th>
                            <th class="px-8 py-5 text-rose-600">Alasan / Kendala</th>
                        </tr>
                    </thead>
                    <tbody id="troubleTable" class="divide-y divide-slate-100 text-sm">
                        <!-- Data row akan di-generate di sini -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const rawData = """ + data_json + """;
        document.getElementById('timestamp').innerText = "Last Sync: " + new Date().toLocaleTimeString();

        function render() {
            let countHijau = 0;
            let countMerah = 0;
            let tableRows = "";

            if (!rawData || rawData.length === 0) {
                document.getElementById('troubleTable').innerHTML = '<tr><td colspan="3" class="px-8 py-20 text-center text-slate-400 italic">Database Kosong</td></tr>';
                return;
            }

            rawData.forEach(item => {
                const keys = Object.keys(item);
                
                // TRIGGER UTAMA: NPSN
                // Pastikan NPSN ada dan tidak kosong
                const npsn = (item[keys[0]] || "").toString().trim();
                
                // Jika NPSN tidak ada, baris ini diabaikan sama sekali
                if (!npsn || npsn === "" || npsn === "-") return;

                const nama = item[keys[1]] || "Tanpa Nama";
                const status = (item[keys[2]] || "").toString().toLowerCase().trim();
                const reason = item[keys[3]] || "N/A";

                // Logika Hitung Berdasarkan Status
                if (status === 'hijau') {
                    countHijau++;
                } else if (status === 'merah') {
                    countMerah++;
                    tableRows += `
                        <tr class="hover:bg-rose-50/40 transition-all">
                            <td class="px-8 py-5 font-bold text-indigo-600 tracking-tight">#\${npsn}</td>
                            <td class="px-8 py-5 font-semibold text-slate-700">\${nama}</td>
                            <td class="px-8 py-5">
                                <div class="flex items-center gap-2 bg-rose-50 text-rose-700 px-3 py-1.5 rounded-xl border border-rose-100 font-medium italic text-xs">
                                    <i data-lucide="x-circle" size="14"></i> \${reason}
                                </div>
                            </td>
                        </tr>
                    `;
                }
            });

            // Update statistik di UI
            document.getElementById('installedCount').innerText = countHijau;
            document.getElementById('troubleCount').innerText = countMerah;
            
            // Update tabel trouble
            const tableBody = document.getElementById('troubleTable');
            tableBody.innerHTML = tableRows || `
                <tr>
                    <td colspan="3" class="px-8 py-20 text-center">
                        <div class="flex flex-col items-center gap-3 text-emerald-500 opacity-60">
                            <i data-lucide="smile" size="48"></i>
                            <span class="font-bold text-sm">Tidak ada data trouble yang terdeteksi melalui NPSN</span>
                        </div>
                    </td>
                </tr>`;
            
            lucide.createIcons();
        }

        document.addEventListener('DOMContentLoaded', render);
    </script>
</body>
</html>
"""

# Render komponen HTML ke dalam Streamlit
components.html(html_code, height=1200, scrolling=True)

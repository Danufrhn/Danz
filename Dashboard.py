import streamlit as st
import streamlit.components.v1 as components

# Pastikan file Python dimulai dengan kode Python, bukan tag <script>
st.set_page_config(
    page_title="Dashboard Monitoring Pemasangan Sekolah",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Masukkan link CSV Google Sheets Anda di bawah ini
# Cara: File -> Share -> Publish to web -> CSV
URL_SPREADSHEET = "https://docs.google.com/spreadsheets/d/e/2PACX-1v.../pub?gid=0&single=true&output=csv"

html_code = f"""
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
        body {{ font-family: 'Inter', sans-serif; }}
        .glass-card {{ background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(10px); }}
    </style>
</head>
<body class="bg-slate-50 min-h-screen p-4 md:p-8">

    <div class="max-w-6xl mx-auto">
        <!-- Header -->
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
            <div>
                <h1 class="text-3xl font-extrabold text-slate-800 flex items-center gap-2">
                    <i data-lucide="monitor" class="text-blue-600"></i>
                    Dashboard Monitoring Sekolah
                </h1>
                <p class="text-slate-500">Status Pemasangan Real-time dari Spreadsheet</p>
            </div>
            <button onclick="window.location.reload()" class="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-all shadow-lg shadow-blue-200">
                <i data-lucide="refresh-cw" size="18"></i> Refresh Data
            </button>
        </div>

        <!-- Statistik Utama -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div class="glass-card p-6 rounded-2xl border border-emerald-100 shadow-sm flex items-center gap-5">
                <div class="bg-emerald-500 p-4 rounded-xl text-white shadow-lg shadow-emerald-200">
                    <i data-lucide="check-circle-2" size="32"></i>
                </div>
                <div>
                    <p class="text-sm font-semibold text-slate-400 uppercase tracking-wider">Terpasang (Hijau)</p>
                    <h2 id="installedCount" class="text-4xl font-bold text-emerald-600">0</h2>
                </div>
            </div>

            <div class="glass-card p-6 rounded-2xl border border-rose-100 shadow-sm flex items-center gap-5">
                <div class="bg-rose-500 p-4 rounded-xl text-white shadow-lg shadow-rose-200">
                    <i data-lucide="alert-triangle" size="32"></i>
                </div>
                <div>
                    <p class="text-sm font-semibold text-slate-400 uppercase tracking-wider">Bermasalah (Merah)</p>
                    <h2 id="troubleCount" class="text-4xl font-bold text-rose-600">0</h2>
                </div>
            </div>
        </div>

        <!-- Tabel Detail -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
            <div class="p-6 border-b border-slate-100 flex justify-between items-center">
                <h3 class="text-xl font-bold text-slate-800 flex items-center gap-2">
                    <i data-lucide="list-x" class="text-rose-500"></i>
                    Daftar Sekolah Trouble
                </h3>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left">
                    <thead class="bg-slate-50 text-slate-500 text-xs uppercase font-bold tracking-widest">
                        <tr>
                            <th class="px-6 py-4">NPSN</th>
                            <th class="px-6 py-4">Nama Sekolah</th>
                            <th class="px-6 py-4 text-rose-600">Alasan Kerusakan (Reason)</th>
                        </tr>
                    </thead>
                    <tbody id="troubleTable" class="divide-y divide-slate-100">
                        <tr><td colspan="3" class="px-6 py-10 text-center text-slate-400 italic">Memuat data...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const CSV_URL = "{URL_SPREADSHEET}";

        async function init() {{
            try {{
                const response = await fetch(CSV_URL);
                const data = await response.text();
                const rows = data.split('\\n').slice(1);
                
                let installed = 0;
                let trouble = 0;
                let troubleHtml = "";

                rows.forEach(row => {{
                    const cols = row.split(',');
                    if (cols.length < 3) return;

                    const npsn = cols[0].trim();
                    const nama = cols[1].trim();
                    const warna = cols[2].toLowerCase().trim(); // Trigger: 'hijau' atau 'merah'
                    const reason = cols[3] ? cols[3].trim() : "-";

                    if (warna === 'hijau') {{
                        installed++;
                    }} else if (warna === 'merah') {{
                        trouble++;
                        troubleHtml += `
                            <tr class="hover:bg-rose-50/50 transition-colors">
                                <td class="px-6 py-4 font-mono text-sm font-bold text-slate-600">#\${npsn}</td>
                                <td class="px-6 py-4 font-semibold text-slate-800">\${nama}</td>
                                <td class="px-6 py-4 text-rose-600 italic font-medium">
                                    <span class="inline-flex items-center gap-1 bg-rose-50 px-2 py-1 rounded border border-rose-100">
                                        <i data-lucide="info" size="14"></i> \${reason}
                                    </span>
                                </td>
                            </tr>
                        `;
                    }}
                }});

                document.getElementById('installedCount').innerText = installed;
                document.getElementById('troubleCount').innerText = trouble;
                
                const tableBody = document.getElementById('troubleTable');
                if (troubleHtml === "") {{
                    tableBody.innerHTML = '<tr><td colspan="3" class="px-6 py-10 text-center text-emerald-500 font-medium">Semua sekolah dalam kondisi baik.</td></tr>';
                }} else {{
                    tableBody.innerHTML = troubleHtml;
                }}
                
                lucide.createIcons();
            }} catch (e) {{
                console.error(e);
                document.getElementById('troubleTable').innerHTML = '<tr><td colspan="3" class="px-6 py-10 text-center text-rose-500">Gagal menyambungkan ke Google Sheets. Pastikan URL benar dan di-publish ke web.</td></tr>';
            }}
        }}

        init();
        lucide.createIcons();
    </script>
</body>
</html>
"""

components.html(html_code, height=1000, scrolling=True)

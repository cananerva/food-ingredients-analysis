const API_BASE = "http://127.0.0.1:8000";

const ingredientsInput = document.getElementById("ingredientsInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const resultDiv = document.getElementById("result");
const statusText = document.getElementById("statusText");
const imageInput = document.getElementById("imageInput");
const analyzeImageBtn = document.getElementById("analyzeImageBtn");
const ocrTextDiv = document.getElementById("ocrText");

function getRiskColor(risk) {
  if (!risk) return "";
  const r = risk.toLowerCase();
  if (r === "düşük" || r === "dusuk") return "background:#d1fae5;";     
  if (r === "orta") return "background:#fef9c3;";                      
  if (r === "yüksek" || r === "yuksek") return "background:#fecaca;"; 
  return "";
}

function renderAnalysis(data) {
  if (!data || !Array.isArray(data.items) || data.items.length === 0) {
    resultDiv.innerHTML = "Analiz edilebilecek bir içerik bulunamadı.";
    return;
  }

  let html = "";

  if (data.overall_risk_level) {
    html += `<p><strong>Genel risk seviyesi:</strong> ${data.overall_risk_level}</p>`;
  }

  html += `
    <table>
      <thead>
        <tr>
          <th>İçerik</th>
          <th>Halk Dili Adı</th>
          <th>Kategori</th>
          <th>Risk</th>
          <th>Açıklama</th>
        </tr>
      </thead>
      <tbody>
  `;

  for (const item of data.items) {
    if (item.matched) {
      const riskColor = getRiskColor(item.risk);
      html += `
        <tr>
          <td>${item.ingredient}</td>
          <td>${item.common_name}</td>
          <td>${item.category}</td>
          <td style="${riskColor}">${item.risk}</td>
          <td>${item.description}</td>
        </tr>
      `;
    } else {
      if (item.predicted_risk) {
        const riskColor = getRiskColor(item.predicted_risk);
        html += `
          <tr>
            <td>${item.ingredient}</td>
            <td>-</td>
            <td>-</td>
            <td style="${riskColor}">${item.predicted_risk} (ML)</td>
            <td>${item.info || "Sözlükte yok, ML modeli ile risk tahmini yapıldı."}</td>
          </tr>
        `;
      } else {
        html += `
          <tr>
            <td>${item.ingredient}</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>${item.info || "Bu madde sözlükte bulunamadı."}</td>
          </tr>
        `;
      }
    }
  }

  html += `
      </tbody>
    </table>
  `;

  resultDiv.innerHTML = html;
}

analyzeBtn.addEventListener("click", async () => {
  const text = ingredientsInput.value.trim();

  if (!text) {
    alert("Lütfen içindekiler metni gir.");
    return;
  }

  analyzeBtn.disabled = true;
  statusText.textContent = "Metin analizi yapılıyor...";
  resultDiv.textContent = "";

  try {
    const response = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ingredients: text }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`İstek başarısız: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    renderAnalysis(data);
    statusText.textContent = "Metin analizi tamamlandı.";
  } catch (err) {
    console.error(err);
    statusText.textContent = "Metin analizinde bir hata oluştu.";
    resultDiv.textContent = String(err);
  } finally {
    analyzeBtn.disabled = false;
  }
});

analyzeImageBtn.addEventListener("click", async () => {
  const file = imageInput.files[0];
  if (!file) {
    alert("Lütfen bir resim dosyası seç.");
    return;
  }

  analyzeImageBtn.disabled = true;
  statusText.textContent = "Resimden metin okunuyor ve analiz ediliyor...";
  ocrTextDiv.textContent = "";
  resultDiv.textContent = "";

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(`${API_BASE}/analyze_image`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`İstek başarısız: ${response.status} - ${errorText}`);
    }

    const data = await response.json();

    ocrTextDiv.textContent = data.extracted_text || "(Metin okunamadı)";
    renderAnalysis(data.analysis);

    statusText.textContent = "Resim analizi tamamlandı.";
  } catch (err) {
    console.error(err);
    statusText.textContent = "Resim analizinde bir hata oluştu.";
    resultDiv.textContent = String(err);
  } finally {
    analyzeImageBtn.disabled = false;
  }
});

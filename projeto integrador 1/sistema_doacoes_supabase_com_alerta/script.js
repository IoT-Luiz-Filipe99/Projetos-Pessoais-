
const SUPABASE_URL = "https://bsidxirwwawwmxdyjzww.supabase.co";
const SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJzaWR4aXJ3d2F3d214ZHlqend3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM3OTAwOTgsImV4cCI6MjA2OTM2NjA5OH0.kIHLhQme-lW1Omtk8DudkrxLXIv1zZS5ZJUyEsxoMHo";

const form = document.getElementById('form-doacao');
const tabelaBody = document.querySelector('#tabela-doacoes tbody');
const graficoCtx = document.getElementById('graficoDoacoes').getContext('2d');
let dadosGrafico = { Alimento: 0, Roupa: 0, Higiene: 0 };

// Atualizar tabela com doações
const atualizarTabela = async () => {
    tabelaBody.innerHTML = '';
    const resposta = await fetch(`${SUPABASE_URL}/rest/v1/doacoes?select=*`, {
        headers: {
            apikey: SUPABASE_API_KEY,
            Authorization: `Bearer ${SUPABASE_API_KEY}`
        }
    });
    const doacoes = await resposta.json();
    doacoes.forEach(d => {
        const row = tabelaBody.insertRow();
        row.innerHTML = `
            <td>${d.nome}</td>
            <td>${d.contato}</td>
            <td>${d.tipo_doacao}</td>
            <td>${d.quantidade}</td>
            <td>${d.data_doacao}</td>
        `;
    });
};

// Atualizar gráfico
const atualizarGrafico = async () => {
    dadosGrafico = { Alimento: 0, Roupa: 0, Higiene: 0 };
    const resposta = await fetch(`${SUPABASE_URL}/rest/v1/doacoes?select=tipo_doacao,quantidade`, {
        headers: {
            apikey: SUPABASE_API_KEY,
            Authorization: `Bearer ${SUPABASE_API_KEY}`
        }
    });
    const doacoes = await resposta.json();
    doacoes.forEach(d => {
        if (dadosGrafico[d.tipo_doacao] !== undefined) {
            dadosGrafico[d.tipo_doacao] += parseInt(d.quantidade);
        }
    });
    grafico.data.datasets[0].data = Object.values(dadosGrafico);
    grafico.update();
};

// Enviar nova doação
form.addEventListener('submit', async e => {
    e.preventDefault();
    const novaDoacao = {
        nome: form.nome.value,
        contato: form.contato.value,
        tipo_doacao: form['tipo-doacao'].value,
        quantidade: parseInt(form.quantidade.value),
        data_doacao: form.data.value
    };

    const resposta = await fetch(`${SUPABASE_URL}/rest/v1/doacoes`, {
        method: 'POST',
        headers: {
            apikey: SUPABASE_API_KEY,
            Authorization: `Bearer ${SUPABASE_API_KEY}`,
            'Content-Type': 'application/json',
            Prefer: 'return=minimal'
        },
        body: JSON.stringify(novaDoacao)
    });

    if (resposta.ok) {
        alert("✅ Doação cadastrada com sucesso!");
        form.reset();
        atualizarTabela();
        atualizarGrafico();
    } else {
        alert("❌ Erro ao cadastrar doação. Verifique o console.");
        console.error(await resposta.text());
    }
});

// Gráfico inicial
const grafico = new Chart(graficoCtx, {
    type: 'bar',
    data: {
        labels: ['Alimento', 'Roupa', 'Higiene'],
        datasets: [{
            label: 'Total por Tipo de Doação',
            data: [0, 0, 0],
            backgroundColor: ['#4CAF50', '#2196F3', '#FFC107']
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// Inicializar
atualizarTabela();
atualizarGrafico();

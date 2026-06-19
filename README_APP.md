# AGM Performance — Sistema de Gestión de Service

## Cómo ejecutar la app

```bash
cd agm_app
pip install -r requirements.txt
streamlit run app.py
```

Luego abrir en el navegador: http://localhost:8501

## Estructura

```
agm_app/
├── app.py              # Punto de entrada Streamlit
├── database.py         # Operaciones SQLite
├── pdf_export.py       # Generador de PDF (Diseño Professional White)
├── agm_service.db      # Base de datos (se crea al primer uso)
├── pdfs/               # PDFs generados por orden
├── requirements.txt
├── .streamlit/
│   └── config.toml     # Tema rojo/blanco AGM
└── pages/
    ├── dashboard.py    # Panel de estadísticas
    ├── nueva_ficha.py  # Formulario de carga
    ├── historial.py    # Historial de servicios
    └── clientes.py     # Gestión de clientes
```

## Funcionalidades

- **Dashboard**: KPIs, servicios por mes, facturación, top clientes, trabajos más solicitados, marcas más atendidas
- **Nueva Ficha**: Carga completa de service (cliente, moto, trabajos, inspección, ECU, presupuesto) + PDF automático
- **Historial**: Búsqueda por cliente/moto/estado/fecha, detalle completo, cambio de estado, descarga PDF
- **Clientes**: Lista de clientes con historial de motos y servicios, facturación por cliente

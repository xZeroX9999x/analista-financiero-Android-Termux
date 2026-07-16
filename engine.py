# engine.py
import time
from datetime import datetime
from typing import Optional, List

from yahooquery import Ticker
from groq import Groq

from config import logger, MAX_RETRIES, BACKOFF_FACTOR
from models import DatosFinancieros, TelemetriaMercado, Noticia, ReporteFinal
from cache import CacheManager

cache = CacheManager()

class MotorExtraccion:
    def __init__(self, api_key: Optional[str] = None):
        self.groq_client = None
        
        if api_key:
            try:
                self.groq_client = Groq(api_key=api_key)
                logger.info("✅ Cliente Groq inicializado")
            except Exception as e:
                logger.error(f"❌ Error inicializando Groq: {e}")
    
    def _reintentar(self, func, *args, **kwargs):
        last_exception = None
        for intento in range(MAX_RETRIES):
            try: return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                wait_time = BACKOFF_FACTOR ** intento
                if intento < MAX_RETRIES - 1:
                    time.sleep(wait_time)
        logger.error(f"❌ Intentos agotados. Error: {last_exception}")
        return None
    
    def obtener_fundamentales(self, ticker: str) -> Optional[DatosFinancieros]:
        cached = cache.get('fund', ticker)
        if cached: return DatosFinancieros(**cached)
        
        logger.info(f"📊 Extrayendo Fundamentales de la matriz financiera para {ticker}...")
        def _fetch():
            yq = Ticker(ticker)
            try:
                inc = yq.income_statement()
                bal = yq.balance_sheet()
                cf = yq.cash_flow()
                
                if isinstance(inc, str) or isinstance(bal, str):
                    return None

                inc_dict = inc.to_dict('records')[-1] if not inc.empty else {}
                bal_dict = bal.to_dict('records')[-1] if not bal.empty else {}
                cf_dict = cf.to_dict('records')[-1] if not isinstance(cf, str) and not cf.empty else {}

                datos = DatosFinancieros(
                    revenue=inc_dict.get('TotalRevenue', 0),
                    net_income=inc_dict.get('NetIncome', 0),
                    total_assets=bal_dict.get('TotalAssets', 0),
                    total_liabilities=bal_dict.get('TotalLiabilitiesNetMinorityInterest', bal_dict.get('TotalLiabilities', 0)),
                    free_cash_flow=cf_dict.get('FreeCashFlow', 0),
                    operating_cash_flow=cf_dict.get('OperatingCashFlow', 0),
                    capital_expenditure=cf_dict.get('CapitalExpenditure', 0)
                )
                cache.set('fund', ticker, datos)
                return datos
            except Exception as e:
                logger.warning(f"⚠️ Error procesando fundamentales: {e}")
                return None
                
        return self._reintentar(_fetch)
    
    def obtener_yahoo(self, ticker: str) -> Optional[TelemetriaMercado]:
        cached = cache.get('yahoo', ticker)
        if cached: return TelemetriaMercado(**cached)
        
        logger.info(f"📈 Obteniendo telemetría de mercado para {ticker}...")
        def _fetch():
            yq = Ticker(ticker)
            stats = yq.key_stats.get(ticker, {})
            price = yq.price.get(ticker, {})
            if not isinstance(stats, dict) or not isinstance(price, dict): return None
            
            datos = TelemetriaMercado(
                enterprise_value=stats.get('enterpriseValue', 0),
                forward_pe=stats.get('forwardPE', 0), profit_margins=stats.get('profitMargins', 0),
                current_price=price.get('regularMarketPrice', 0), market_cap=stats.get('marketCap', 0),
                dividend_yield=stats.get('dividendYield', 0)
            )
            cache.set('yahoo', ticker, datos)
            return datos
        return self._reintentar(_fetch)
    
    def obtener_noticias(self, ticker: str) -> List[Noticia]:
        cached = cache.get('news', ticker)
        if cached: return [Noticia(**n) for n in cached]
        
        logger.info(f"📰 Compilando OSINT para {ticker}...")
        try:
            yq = Ticker(ticker)
            noticias_yahoo = getattr(yq, 'news', [])
            if callable(noticias_yahoo): noticias_yahoo = noticias_yahoo()
            if isinstance(noticias_yahoo, dict): noticias_yahoo = noticias_yahoo.get(ticker, [])
            if not noticias_yahoo or not isinstance(noticias_yahoo, list): return []
            
            resultados = []
            for n in noticias_yahoo[:5]:
                titulo, fuente, url, fecha = "", "Yahoo", "#", None
                if isinstance(n, dict):
                    titulo = n.get('title', '').strip()
                    fuente = n.get('publisher', 'Yahoo Finance')
                    url = n.get('link', '#')
                    raw_fecha = n.get('providerPublishTime')
                    if raw_fecha: fecha = datetime.fromtimestamp(raw_fecha).strftime('%Y-%m-%d')
                elif isinstance(n, str): titulo = n.strip()
                
                if not titulo or titulo.lower() in ['error', 'not found']: continue
                resultados.append(Noticia(titulo=titulo, fuente=fuente, url=url, fecha=fecha))
            
            cache.set('news', ticker, [n.model_dump() for n in resultados])
            return resultados
        except: return []
    
    def analizar(self, ticker: str) -> ReporteFinal:
        logger.info(f"🔍 Evaluando Ticker: {ticker}...")
        fundamentales_data = self.obtener_fundamentales(ticker)
        mkt_data = self.obtener_yahoo(ticker)
        noticias = self.obtener_noticias(ticker)
        
        return ReporteFinal(
            ticker=ticker.upper(), fecha=datetime.now().strftime("%Y-%m-%d"),
            fundamentales=fundamentales_data, mercado=mkt_data, noticias=noticias,
            metadata={'timestamp': datetime.now().isoformat(), 'origen': 'Termux_Optimizado_Nativo'}
        )
    
    def generar_analisis_ia(self, reporte: ReporteFinal) -> str:
        if not self.groq_client: return self._analisis_heuristico_local(reporte)
        
        logger.info("🤖 Ejecutando IA con Prompt Estructurado...")
        
        prompt = f"""<Rol>Eres un analista financiero senior experto en valoración de activos de Wall Street.</Rol>
<Mision>Evalúa los datos matemáticos proporcionados y genera un reporte estructurado y conciso.</Mision>

<Contexto>
Datos inmutables extraídos de {reporte.ticker}:
{reporte.model_dump_json(indent=2)}
</Contexto>

<Instrucciones>
DEBES generar el análisis estrictamente con la siguiente estructura:
1. Fundamentales del Negocio
- Ventas y Rentabilidad: Analiza la facturación y beneficio neto.
- Márgenes y Solvencia: Evalúa margen de beneficio y ratio activo/pasivo.
- Flujos de Caja: Analiza el efectivo disponible.

2. Valoración de Mercado
- Capitalización y Múltiplos: Analiza precio vs valor real (PE y Enterprise Value).
- Dividendos (Si aplica).

3. Impacto de OSINT y Noticias
- Integra las noticias recientes como catalizadores positivos o negativos.

Conclusión: Declara claramente si recomiendas Invertir, Mantener o Vender.
</Instrucciones>

<Restricciones>
- NO uses frases de cortesía. Ve directo al punto.
- Serás penalizado si inventas o alucinas información externa a <Contexto>.
</Restricciones>

<Incentivo>¡Voy a dar una propina de $300,000 por el mejor y más preciso análisis estructurado!</Incentivo>"""

        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Analista IA activado. Modo estricto."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=2000
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.warning(f"⚠️ Caída de API. Activando motor heurístico local... ({e})")
            return self._analisis_heuristico_local(reporte)
    
    def _analisis_heuristico_local(self, reporte: ReporteFinal) -> str:
        logger.info("📊 Fallback: Ejecutando Motor Heurístico...")
        lineas = [f"\n=== ANÁLISIS HEURÍSTICO AUTOMATIZADO: {reporte.ticker} ({reporte.fecha}) ===\n"]
        
        if reporte.fundamentales:
            f = reporte.fundamentales
            lineas.append("1. FUNDAMENTALES FINANCIEROS")
            lineas.append(f"   - Ingresos (Revenue): ${f.revenue:,.2f}")
            lineas.append(f"   - Beneficio Neto: ${f.net_income:,.2f}")
            if f.revenue > 0:
                margen = (f.net_income / f.revenue) * 100
                lineas.append(f"   - Margen de Beneficio: {margen:.2f}%")
            lineas.append(f"   - Activos Totales: ${f.total_assets:,.2f}")
            lineas.append(f"   - Pasivos Totales: ${f.total_liabilities:,.2f}")
            if f.total_liabilities > 0:
                ratio = f.total_assets / f.total_liabilities
                lineas.append(f"   - Ratio de Solvencia (A/P): {ratio:.2f}x")
            lineas.append(f"   - Flujo de Caja Libre: ${f.free_cash_flow:,.2f}")
        else:
            lineas.append("1. FUNDAMENTALES: No disponibles")
        
        if reporte.mercado:
            m = reporte.mercado
            lineas.append("\n2. TELEMETRÍA DE MERCADO")
            lineas.append(f"   - Precio Actual: ${m.current_price:,.2f}")
            lineas.append(f"   - Enterprise Value: ${m.enterprise_value:,.2f}")
            if m.forward_pe: lineas.append(f"   - Forward P/E: {m.forward_pe:.2f}x")
            if m.dividend_yield: lineas.append(f"   - Dividend Yield: {m.dividend_yield * 100:.2f}%")
        
        if reporte.noticias:
            lineas.append("\n3. RADAR DE NOTICIAS (OSINT)")
            for n in reporte.noticias:
                fecha_str = f" [{n.fecha}]" if n.fecha else ""
                lineas.append(f"   - {n.titulo} ({n.fuente}){fecha_str}")
                
        return "\n".join(lineas)

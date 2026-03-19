from typing import List

def get_search_queries(uf: str, estado: str) -> List[str]:
    return [
        # Base legal direta
        f'"Lei 13.019" {estado}',
        f'marco regulatório organizações sociedade civil {estado}',
        f'MROSC {estado} regulamentação',

        # Decretos e normativas
        f'decreto regulamenta lei 13.019 {estado}',
        f'decreto parcerias OSC {estado}',
        f'instrução normativa MROSC {estado}',
        f'resolução parcerias sociedade civil {estado}',
        f'portaria parcerias OSC {estado}',

        # Instrumentos operacionais
        f'manual parcerias OSC {estado}',
        f'guia MROSC {estado}',
        f'cartilha organizações sociedade civil {estado}',
        f'fluxo prestação de contas OSC {estado}',

        # Sistemas e gestão
        f'sistema gestão parcerias OSC {estado}',
        f'plataforma parcerias governo {estado}',
        f'chamamento público OSC {estado}',

        # Transparência e controle
        f'diário oficial {estado} organizações sociedade civil',
        f'transferências voluntárias OSC {estado}',
        f'prestação de contas parceria OSC {estado}',

        # Busca restrita a domínios oficiais
        f'site:{uf.lower()}.gov.br "organizações da sociedade civil"',
        f'site:{uf.lower()}.gov.br "parcerias"',
        f'site:{uf.lower()}.gov.br "chamamento público"',
        
        # Queries com a liguagem da burocracia
        f'"termo de colaboração" {estado}',
        f'"termo de fomento" {estado}',
        f'"acordo de cooperação" OSC {estado}',
        f'"comissão de monitoramento" OSC {estado}',

        # Queries orientadas ao seu framework analítico
        f'monitoramento avaliação parcerias OSC {estado}',
        f'capacitação OSC governo {estado}',
        f'governança parcerias sociedade civil {estado}',
        f'fluxo administrativo parcerias OSC {estado}',
        f'indicadores parceria governo OSC {estado}'
    ]

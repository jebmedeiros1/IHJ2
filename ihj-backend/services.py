import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from database import execute_insert, execute_query
import logging
from models import FiltroRequest, SimilaridadeRequest


logger = logging.getLogger(__name__)

class equipamentoService:
    """Serviço para operações relacionadas a equipamentos"""
    
    def __init__(self):
        # Carrega o de/para de classes a partir da tabela dbo.tb_classes
        try:
            query = "SELECT id, nome FROM dbo.tb_classes"
            self.df_depara_classe = execute_query(query)
            if not self.df_depara_classe.empty:
                self.classe_dict = dict(zip(self.df_depara_classe["nome"], self.df_depara_classe["id"]))
                self.classe_reverse_dict = dict(zip(self.df_depara_classe["id"], self.df_depara_classe["nome"]))
            else:
                self.classe_dict = {}
                self.classe_reverse_dict = {}
        except Exception:
            self.df_depara_classe = pd.DataFrame()
            self.classe_dict = {}
            self.classe_reverse_dict = {}
    

    def get_classes(self) -> Dict[str, str]:
        """Obtém mapeamento de id para nome das classes"""
        try:
            df_classes = execute_query(
                "SELECT id, nome FROM dbo.tb_classes ORDER BY nome"
            )

            return {
                str(int(row["id"])): row["nome"]
                for _, row in df_classes.iterrows()
            }

        except Exception as e:
            raise Exception(f"Erro ao carregar classes: {e}")

    #def get_classes(self) -> List[str]:
    #    """Obtém lista de classes disponíveis"""
    #    try:
    #        df_classes = execute_query('SELECT DISTINCT classe FROM dbo.tb_caract')
    #        classes_validas = df_classes['nome'].astype(str).tolist()
    #        
    #        # Retorna nomes das classes se houver de/para, senão retorna IDs
     #       if self.classe_reverse_dict:
     #           return [self.classe_reverse_dict[c] for c in classes_validas if c in self.classe_reverse_dict]
    #        else:
    #            return classes_validas
     #   except Exception as e:
    #        raise Exception(f"Erro ao carregar classes: {e}")
    #
    def get_caracteristicas(self, classes: List[str]) -> List[str]:
        """Obtém características disponíveis para as classes selecionadas"""
        try:
            # Converte nomes para IDs se necessário
            if self.classe_dict:
                class_ids = [self.classe_dict.get(c, c) for c in classes]
            else:
                class_ids = classes
            
            class_filter = ", ".join([f"'{c}'" for c in class_ids])
            query = f"SELECT DISTINCT ds_caracteristica FROM dbo.tb_caract WHERE classe IN ({class_filter})"
            
            df_columns = execute_query(query)
            return df_columns['ds_caracteristica'].tolist()
        except Exception as e:
            raise Exception(f"Erro ao carregar características: {e}")
    
    def get_valores_caracteristica(self, caracteristica: str, classes: List[str]) -> List[str]:
        """Obtém valores disponíveis para uma característica específica"""
        try:
            # Converte nomes para IDs se necessário
            if self.classe_dict:
                class_ids = [self.classe_dict.get(c, c) for c in classes]
            else:
                class_ids = classes
            
            class_filter = ", ".join([f"'{c}'" for c in class_ids])
            query = f"""
                SELECT DISTINCT valor 
                FROM dbo.tb_caract 
                WHERE ds_caracteristica = '{caracteristica}' 
                AND classe IN ({class_filter}) 
                ORDER BY valor
            """
            
            df_values = execute_query(query)
            return df_values['valor'].fillna("None").tolist()
        except Exception as e:
            raise Exception(f"Erro ao carregar valores para {caracteristica}: {e}")
    
    def filtrar_equipamentos(self, filtro_request: FiltroRequest) -> Dict[str, Any]:
        """Filtra equipamentos com base nos critérios especificados"""
        try:
            # Converte nomes para IDs se necessário
            if self.classe_dict:
                class_ids = [self.classe_dict.get(c, c) for c in filtro_request.classes]
            else:
                class_ids = filtro_request.classes
            
            class_filter = ", ".join([f"'{c}'" for c in class_ids])
            
            # Constrói condições de filtro
            filter_conditions = []
            for col, values in filtro_request.filtros.items():
                conditions = []
                for val in values:
                    if val == "None" or val is None:
                        conditions.append("valor IS NULL")
                    else:
                        conditions.append(f"valor = '{val}'")
                
                filter_conditions.append(
                    f"EXISTS (SELECT 1 FROM dbo.tb_caract AS T2 "
                    f"WHERE T2.equipamento = dbo.tb_caract.equipamento "
                    f"AND ds_caracteristica = '{col}' "
                    f"AND ({' OR '.join(conditions)}))"
                )
            
            # Query final
            final_query = f"""
                SELECT DISTINCT equipamento 
                FROM dbo.tb_caract 
                WHERE classe IN ({class_filter}) 
                AND {' AND '.join(filter_conditions)}
            """
            
            filtered_df = execute_query(final_query)
            
            if filtered_df.empty:
                return {
                    "equipamentos": [],
                    "dados_pivot": None,
                    "message": "Nenhum equipamento encontrado com os filtros aplicados."
                }
            
            # Insere na tabela temporária
            resultado_insercao = execute_insert(filtered_df, "dbo.tb_temp")
            
            # Busca dados completos
            query_completa = "SELECT * FROM dbo.tb_caract  WHERE equipamento IN (SELECT equipamento FROM dbo.tb_temp)"
            df_completo = execute_query(query_completa)
            df_completo['valor'] = df_completo['valor'].fillna("None")
            
            # Cria pivot table
            dados_pivot = None
            detalhes_completos = None
            if not df_completo.empty:
                df_pivot = df_completo.pivot_table(
                    index='ds_caracteristica',
                    columns=['equipamento', 'centro', 'classe'],
                    values='valor',
                    aggfunc='first'
                )
                dados_pivot = df_pivot.to_dict()

                # Estrutura detalhes completos para cada equipamento
                df_det = df_completo.pivot_table(
                    index=['equipamento', 'centro', 'classe'],
                    columns='ds_caracteristica',
                    values='valor',
                    aggfunc='first'
                ).reset_index()
                detalhes_completos = df_det.to_dict('records')
            
            # Lista de equipamentos
            equipamentos = []
            for _, row in filtered_df.iterrows():
                equipamentos.append({
                    "equipamento": row['equipamento']
                })
            
            return {
                "equipamentos": equipamentos,
                "dados_pivot": dados_pivot,
                "detalhes_completos": detalhes_completos,
                "message": f"Encontrados {len(equipamentos)} equipamentos."
            }
            
        except Exception as e:
            raise Exception(f"Erro ao filtrar equipamentos: {e}")

class SimilaridadeService:
    """Serviço para análise de similaridade de equipamentos"""
    
    def __init__(self):
        # Carrega informações dos equipamentos a partir da tabela dbo.tb_equipamentos
        try:
            self.df_info = execute_query("SELECT * FROM dbo.tb_equipamentos")
        except Exception:
            self.df_info = pd.DataFrame()
    
    def calculate_similarity(self, df: pd.DataFrame, target_equipment: str) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """Calcula similaridade entre equipamentos"""
        target_row = df[df['equipamento'] == target_equipment]
        
        if target_row.empty:
            return None, None
        
        target_row_data = target_row.drop(columns=['equipamento']).iloc[0]
        aligned_df = df.drop(columns=['equipamento']).reindex(columns=target_row_data.index)
        
        comparison = aligned_df.apply(lambda row: row == target_row_data, axis=1)
        similarity_score = comparison.sum(axis=1)
        
        # Aplica regras especiais para grupos PMM e PME
        if 'PMM_GRUPO' in df.columns:
            df['Similarity_Score'] = similarity_score
            grupo_alvo = target_row['PMM_GRUPO'].values[0]
            df.loc[df['PMM_GRUPO'] == grupo_alvo, 'Similarity_Score'] = 99
        elif 'PME_GRUPO' in df.columns:
            df['Similarity_Score'] = similarity_score
            grupo_alvo = target_row['PME_GRUPO'].values[0]
            df.loc[df['PME_GRUPO'] == grupo_alvo, 'Similarity_Score'] = 99
        else:
            df['Similarity_Score'] = similarity_score
        
        similar_options = df[df['equipamento'] != target_equipment].sort_values(by='Similarity_Score', ascending=False)
        return similar_options, target_row
    
    def analisar_similaridade(self, request: SimilaridadeRequest) -> Dict[str, Any]:
        """Analisa equipamentos similares ao equipamento alvo"""
        try:
            target_equipment = request.equipamento.upper()
            qtd = request.quantidade
            
            # Verifica se o equipamento existe
            query_check = f"SELECT * FROM dbo.tb_caract WHERE equipamento = '{target_equipment}'"
            df_caract = execute_query(query_check)
            
            if df_caract.empty:
                return {
                    "equipamento_alvo": target_equipment,
                    "equipamentos_similares": [],
                    "detalhes_completos": None,
                    "message": "equipamento alvo não encontrado na base de dados."
                }
            
            # Busca todos os equipamentos da mesma classe
            query_global = f"""
                SELECT * FROM dbo.tb_caract 
                WHERE classe IN (SELECT classe FROM dbo.tb_caract WHERE equipamento = '{target_equipment}')
            """
            df_global = execute_query(query_global)
            
            # Cria pivot table
            df_pivot = df_global.pivot_table(
                index=['equipamento', 'centro', 'classe'], 
                columns='id_caracteristica', 
                values='valor', 
                aggfunc='first'
            )
            df_reset = df_pivot.reset_index()
            
            # Calcula similaridade
            similar_options, target_row = self.calculate_similarity(df_reset, target_equipment)
            
            if similar_options is None:
                return {
                    "equipamento_alvo": target_equipment,
                    "equipamentos_similares": [],
                    "detalhes_completos": None,
                    "message": "Erro ao calcular similaridade."
                }
            
            # Prepara lista de equipamentos similares
            top_similares = similar_options[['equipamento', 'Similarity_Score']].head(qtd)
            equipamentos_similares = []
            
            for _, row in top_similares.iterrows():
                equipamentos_similares.append({
                    "equipamento": row['equipamento'],
                    "similarity_score": float(row['Similarity_Score']),
                    "centro": row.get('centro'),
                    "classe": row.get('Classe')
                })
            
            # Prepara detalhes completos
            target_row['Similarity_Score'] = 'Similaridade'
            detailed_view = pd.concat([target_row, similar_options.head(qtd)])
            
            # Merge com informações adicionais se disponível
            detalhes_completos = None
            if not self.df_info.empty:
                equip_usados = detailed_view['equipamento'].unique()
                df_info_filtrado = self.df_info[self.df_info['Equipam.'].isin(equip_usados)]
                df_merged = detailed_view.merge(self.df_info, left_on='equipamento', right_on='Equipam.', how='left')
                df_merged = df_merged.drop(columns=['Equipam.'])
                detalhes_completos = df_merged.T.to_dict()
            else:
                detalhes_completos = detailed_view.T.to_dict()
            
            return {
                "equipamento_alvo": target_equipment,
                "equipamentos_similares": equipamentos_similares,
                "detalhes_completos": detalhes_completos,
                "message": f"Encontrados {len(equipamentos_similares)} equipamentos similares."
            }
            
        except Exception as e:
            raise Exception(f"Erro ao analisar similaridade: {e}")

# Instâncias dos serviços
equipamento_service = equipamentoService()
similaridade_service = SimilaridadeService()


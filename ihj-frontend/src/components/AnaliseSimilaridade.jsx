import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Search, BarChart3 } from 'lucide-react';
import { similaridadeAPI } from '@/lib/api';

export default function AnaliseSimilaridade() {
  const [equipamentoAlvo, setEquipamentoAlvo] = useState('');
  const [quantidade, setQuantidade] = useState(10);
  const [resultados, setResultados] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const buscarSimilares = async () => {
    if (!equipamentoAlvo.trim()) {
      setError('Digite o código do equipamento');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await similaridadeAPI.getEquipamentosSimilares(
        equipamentoAlvo.toUpperCase(),
        quantidade
      );
      setResultados(response);
    } catch (err) {
      console.error('Erro ao buscar equipamentos similares:', err);
      if (err.response?.status === 404) {
        setError('Equipamento não encontrado na base de dados');
      } else {
        setError('Erro ao buscar equipamentos similares');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    buscarSimilares();
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Análise de Similaridade</h2>
        <p className="text-muted-foreground">
          Encontre equipamentos similares a um equipamento específico.
        </p>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Formulário de Busca */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Search className="h-5 w-5" />
            <span>Buscar Equipamentos Similares</span>
          </CardTitle>
          <CardDescription>
            Digite o código do equipamento alvo para encontrar equipamentos similares
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="equipamento">Código do Equipamento</Label>
                <Input
                  id="equipamento"
                  type="text"
                  value={equipamentoAlvo}
                  onChange={(e) => setEquipamentoAlvo(e.target.value)}
                  placeholder="Ex: MTE01241"
                  disabled={loading}
                  className="uppercase"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="quantidade">Número de Registros</Label>
                <Input
                  id="quantidade"
                  type="number"
                  min="1"
                  max="50"
                  value={quantidade}
                  onChange={(e) => setQuantidade(parseInt(e.target.value) || 10)}
                  disabled={loading}
                />
              </div>
            </div>
            
            <Button type="submit" disabled={loading} className="w-full md:w-auto">
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Buscando...
                </>
              ) : (
                <>
                  <Search className="mr-2 h-4 w-4" />
                  Buscar Equipamento
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Resultados */}
      {resultados && (
        <div className="space-y-6">
          {/* Informações do Equipamento Alvo */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5" />
                <span>Equipamento Alvo</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-lg font-semibold">
                {resultados.equipamento_alvo}
              </div>
              <p className="text-muted-foreground">
                Encontrados {resultados.equipamentos_similares?.length || 0} equipamentos similares
              </p>
            </CardContent>
          </Card>

          {/* Lista de Equipamentos Similares */}
          {resultados.equipamentos_similares && resultados.equipamentos_similares.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>Equipamentos Similares</CardTitle>
                <CardDescription>
                  Ordenados por score de similaridade (maior = mais similar)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {resultados.equipamentos_similares.map((equipamento, index) => (
                    <div 
                      key={index} 
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <div className="flex-1">
                        <div className="font-medium">
                          {equipamento.equipamento}
                        </div>
                        {(equipamento.centro || equipamento.classe) && (
                          <div className="text-sm text-muted-foreground">
                            {equipamento.centro && `Centro: ${equipamento.centro}`}
                            {equipamento.centro && equipamento.classe && ' • '}
                            {equipamento.classe && `Classe: ${equipamento.classe}`}
                          </div>
                        )}
                      </div>
                      <div className="text-right">
                        <div className="font-semibold text-blue-600">
                          Score: {equipamento.similarity_score}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          Similaridade
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="text-center py-8">
                <p className="text-muted-foreground">
                  Nenhum equipamento similar encontrado.
                </p>
              </CardContent>
            </Card>
          )}

          {/* Detalhes Completos */}
          {resultados.detalhes_completos && (
            <Card>
              <CardHeader>
                <CardTitle>Detalhes Completos</CardTitle>
                <CardDescription>
                  Comparação detalhada entre o equipamento alvo e os similares
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground">
                  <p>
                    Dados detalhados disponíveis em formato estruturado. 
                    Uma visualização mais robusta seria implementada com uma tabela 
                    de comparação lado a lado, destacando diferenças e semelhanças.
                  </p>
                  <p className="mt-2">
                    Total de registros de comparação: {Object.keys(resultados.detalhes_completos).length}
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}


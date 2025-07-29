import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Search, Filter } from 'lucide-react';
import { equipamentosAPI } from '@/lib/api';

export default function BuscaCaracteristicas() {
  const [classes, setClasses] = useState({});
  const [selectedClasses, setSelectedClasses] = useState([]);
  const [caracteristicas, setCaracteristicas] = useState([]);
  const [selectedCaracteristicas, setSelectedCaracteristicas] = useState([]);
  const [filtros, setFiltros] = useState({});
  const [valoresCaracteristicas, setValoresCaracteristicas] = useState({});
  const [resultados, setResultados] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Carrega classes disponíveis
  useEffect(() => {
    const loadClasses = async () => {
      try {
        const response = await equipamentosAPI.getClasses();
        setClasses(response.classes || {});
      } catch (err) {
        console.error('Erro ao carregar classes:', err);
        setError('Erro ao carregar classes disponíveis');
      }
    };
    loadClasses();
  }, []);

  // Carrega características quando classes são selecionadas
  useEffect(() => {
    const loadCaracteristicas = async () => {
      if (selectedClasses.length === 0) {
        setCaracteristicas([]);
        setSelectedCaracteristicas([]);
        setFiltros({});
        return;
      }

      try {
        const response = await equipamentosAPI.getCaracteristicas(selectedClasses);
        setCaracteristicas(response.caracteristicas || []);
        setSelectedCaracteristicas([]);
        setFiltros({});
      } catch (err) {
        console.error('Erro ao carregar características:', err);
        setError('Erro ao carregar características');
      }
    };
    loadCaracteristicas();
  }, [selectedClasses]);

  // Carrega valores para uma característica específica
  const loadValoresCaracteristica = async (caracteristica) => {
    if (valoresCaracteristicas[caracteristica]) return;

    try {
      const response = await equipamentosAPI.getValoresCaracteristica(caracteristica, selectedClasses);
      setValoresCaracteristicas(prev => ({
        ...prev,
        [caracteristica]: response.valores || []
      }));
    } catch (err) {
      console.error('Erro ao carregar valores:', err);
      setError(`Erro ao carregar valores para ${caracteristica}`);
    }
  };

  const handleClasseChange = (classeId) => {
    setSelectedClasses(prev => {
      if (prev.includes(classeId)) {
        return prev.filter(c => c !== classeId);
      } else {
        return [...prev, classeId];
      }
    });
  };

  const handleCaracteristicaChange = (caracteristica) => {
    setSelectedCaracteristicas(prev => {
      if (prev.includes(caracteristica)) {
        const newSelected = prev.filter(c => c !== caracteristica);
        const newFiltros = { ...filtros };
        delete newFiltros[caracteristica];
        setFiltros(newFiltros);
        return newSelected;
      } else {
        loadValoresCaracteristica(caracteristica);
        return [...prev, caracteristica];
      }
    });
  };

  const handleFiltroChange = (caracteristica, valor) => {
    setFiltros(prev => {
      const currentValues = prev[caracteristica] || [];
      if (currentValues.includes(valor)) {
        return {
          ...prev,
          [caracteristica]: currentValues.filter(v => v !== valor)
        };
      } else {
        return {
          ...prev,
          [caracteristica]: [...currentValues, valor]
        };
      }
    });
  };

  const aplicarFiltros = async () => {
    if (selectedClasses.length === 0) {
      setError('Selecione pelo menos uma classe');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await equipamentosAPI.filtrarEquipamentos({
        classes: selectedClasses,
        filtros: filtros
      });
      setResultados(response);
    } catch (err) {
      console.error('Erro ao filtrar equipamentos:', err);
      setError('Erro ao filtrar equipamentos');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Busca por Características</h2>
        <p className="text-muted-foreground">
          Filtre equipamentos com base em suas características específicas.
        </p>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Seleção de Classes */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Seleção de Classes</CardTitle>
            <CardDescription>
              Escolha as classes de equipamentos
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {Object.entries(classes).map(([id, nome]) => (
                <div key={id} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id={`classe-${id}`}
                    checked={selectedClasses.includes(id)}
                    onChange={() => handleClasseChange(id)}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor={`classe-${id}`} className="text-sm">
                    {id} - {nome}
                  </Label>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Seleção de Características */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Características</CardTitle>
            <CardDescription>
              Escolha as características para filtrar
            </CardDescription>
          </CardHeader>
          <CardContent>
            {selectedClasses.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                Selecione uma classe primeiro
              </p>
            ) : (
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {caracteristicas.map((caracteristica) => (
                  <div key={caracteristica} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={`carac-${caracteristica}`}
                      checked={selectedCaracteristicas.includes(caracteristica)}
                      onChange={() => handleCaracteristicaChange(caracteristica)}
                      className="rounded border-gray-300"
                    />
                    <Label htmlFor={`carac-${caracteristica}`} className="text-sm">
                      {caracteristica}
                    </Label>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Filtros */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Filtros</CardTitle>
            <CardDescription>
              Selecione valores específicos
            </CardDescription>
          </CardHeader>
          <CardContent>
            {selectedCaracteristicas.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                Selecione características primeiro
              </p>
            ) : (
              <div className="space-y-4 max-h-60 overflow-y-auto">
                {selectedCaracteristicas.map((caracteristica) => (
                  <div key={caracteristica}>
                    <Label className="text-sm font-medium">{caracteristica}</Label>
                    <div className="mt-1 space-y-1 max-h-32 overflow-y-auto">
                      {(valoresCaracteristicas[caracteristica] || []).map((valor) => (
                        <div key={valor} className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id={`valor-${caracteristica}-${valor}`}
                            checked={(filtros[caracteristica] || []).includes(valor)}
                            onChange={() => handleFiltroChange(caracteristica, valor)}
                            className="rounded border-gray-300"
                          />
                          <Label htmlFor={`valor-${caracteristica}-${valor}`} className="text-xs">
                            {valor || 'None'}
                          </Label>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Botão de Aplicar Filtros */}
      <div className="flex justify-center">
        <Button 
          onClick={aplicarFiltros} 
          disabled={loading || selectedClasses.length === 0}
          size="lg"
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Aplicando Filtros...
            </>
          ) : (
            <>
              <Filter className="mr-2 h-4 w-4" />
              Aplicar Filtros
            </>
          )}
        </Button>
      </div>

      {/* Resultados */}
      {resultados && (
        <Card>
          <CardHeader>
            <CardTitle>Resultados da Busca</CardTitle>
            <CardDescription>
              Encontrados {resultados.equipamentos?.length || 0} equipamentos
            </CardDescription>
          </CardHeader>
          <CardContent>
            {resultados.equipamentos && resultados.equipamentos.length > 0 ? (
              <div className="space-y-4">
                <div className="grid gap-2">
                  <h4 className="font-semibold">Equipamentos Encontrados:</h4>
                  <div className="grid gap-1 max-h-40 overflow-y-auto">
                    {resultados.equipamentos.map((eq, index) => (
                      <div key={index} className="text-sm p-2 bg-gray-50 rounded">
                        {eq.equipamento}
                      </div>
                    ))}
                  </div>
                </div>
                
                {resultados.dados_pivot && (
                  <div>
                    <h4 className="font-semibold mb-2">Dados Detalhados:</h4>
                    <div className="text-sm text-muted-foreground">
                      Dados em formato pivot disponíveis (visualização completa seria implementada com uma tabela mais robusta)
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-muted-foreground">
                Nenhum equipamento encontrado com os filtros aplicados.
              </p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}


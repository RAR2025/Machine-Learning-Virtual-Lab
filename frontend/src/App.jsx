import { useMemo, useState } from 'react'
import Header from './components/Header'
import Aim from './components/Aim'
import CodeInput from './components/CodeInput'
import AnalyzeSection from './components/AnalyzeSection'
import CleaningSection from './components/CleaningSection'
import ModelSelection from './components/ModelSelection'
import TrainTestSplit from './components/TrainTestSplit'
import EncodingSection from './components/EncodingSection'
import Conclusion from './components/Conclusion'
import WorkflowStepper from './components/WorkflowStepper'
import { experimentInfo } from './data/experimentData'
import { analyzeCode, cleanData, configureSplit, listModels, selectModel, trainModel } from './services/api'

function App() {
  const [code, setCode] = useState(experimentInfo.dataset.defaultCode);
  const [experimentId, setExperimentId] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [cleaningResults, setCleaningResults] = useState(null);
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState(null);
  const [split, setSplit] = useState(null);
  const [testSize, setTestSize] = useState(0.2);
  const [randomState, setRandomState] = useState(42);
  const [trainMap, setTrainMap] = useState({});
  const [trainingKey, setTrainingKey] = useState(null);
  const [loading, setLoading] = useState('');
  const [error, setError] = useState(null);
  const trainedCount = Object.values(trainMap).filter((x) => x?.result).length;

  const step = useMemo(() => {
    if (trainedCount > 0) return 10;
    if (split) return 6;
    if (selectedModel) return 5;
    if (analysis?.problem_type) return 4;
    if (cleaningResults) return 4;
    if (analysis) return 2;
    return 1;
  }, [trainedCount, split, selectedModel, cleaningResults, analysis]);

  const handleAnalyze = async () => {
    setError(null); setLoading('analyze');
    try {
      const result = await analyzeCode(code, experimentId);
      setExperimentId(result.experiment_id || null);
      setAnalysis(result);
      setCleaningResults(null); setTrainMap({}); setSplit(null);
      setSelectedModel(result.selected_model || null);
      try {
        const m = await listModels(result.experiment_id, result.problem_type);
        setModels(m.models || []);
        setSelectedModel((prev) => prev || m.selected_model || result.selected_model);
      } catch { /* non-fatal */ }
    } catch (e) { setError(e.message); } finally { setLoading(''); }
  };

  const handleClean = async () => {
    setError(null); setLoading('clean');
    try {
      const result = await cleanData(experimentId);
      setExperimentId(result.experiment_id || experimentId);
      setCleaningResults(result);
      setSelectedModel(result.selected_model || selectedModel);
      setModels(result.available_models || models);
    } catch (e) { setError(e.message); } finally { setLoading(''); }
  };

  const handleSelectModel = async (key) => {
    setError(null); setLoading('model');
    try {
      const r = await selectModel(key, experimentId);
      setSelectedModel(r.selected_model);
      setTrainMap({});
    } catch (e) { setError(e.message); } finally { setLoading(''); }
  };

  const handleSplit = async (ts, rs) => {
    setError(null); setLoading('split');
    try {
      const r = await configureSplit(experimentId, ts, rs);
      setSplit(r.split); setTestSize(ts); setRandomState(rs); setTrainMap({});
    } catch (e) { setError(e.message); } finally { setLoading(''); }
  };

  const handleTrain = async (encoding) => {
    setError(null); setLoading('train'); setTrainingKey(encoding);
    try {
      const payload = await trainModel(encoding, {
        experimentId, model: selectedModel, testSize, randomState,
      });
      const res = payload.results;
      const item = Array.isArray(res) ? res.find((x) => (x.encoding_key || "").startsWith(encoding)) || res[0] : res;
      // Store under the requested encoding key so the matching card displays it.
      setTrainMap((prev) => ({ ...prev, [encoding]: item }));
      const s = item?.train_test_split;
      if (s) setSplit({ train_samples: s.train_samples, test_samples: s.test_samples, test_size: s.test_size, random_state: s.random_state, stratified: s.stratified });
    } catch (e) { setError(e.message); } finally { setLoading(''); setTrainingKey(null); }
  };

  const isLoading = loading !== '';

  return (
    <>
      <Header />
      <main>
        {error && <div className="error"><strong>Error:</strong> {error}</div>}
        <Aim />
        <WorkflowStepper current={step} />
        <CodeInput code={code} setCode={setCode} onAnalyze={handleAnalyze} loading={isLoading} />
        <AnalyzeSection analysis={analysis} />
        <CleaningSection result={cleaningResults} onClean={handleClean} loading={isLoading} disabled={!analysis} />
        <ModelSelection problemType={analysis?.problem_type} models={models} selected={selectedModel} onSelect={handleSelectModel} loading={isLoading} />
        <TrainTestSplit split={split} testSize={testSize} randomState={randomState} onApply={handleSplit} loading={isLoading} disabled={!cleaningResults} />
        <EncodingSection onTrain={handleTrain} trainMap={trainMap} loading={isLoading} trainingKey={trainingKey} splitReady={!!(split || cleaningResults)} />
        <Conclusion />
      </main>
    </>
  )
}

export default App

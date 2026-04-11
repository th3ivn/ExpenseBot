import { Component } from 'react';
import type { ReactNode, ErrorInfo } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('[ExpenseBot] Render error:', error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center h-screen bg-bg-primary text-text-primary px-6 text-center">
          <span className="text-4xl mb-4">⚠️</span>
          <h1 className="text-lg font-semibold mb-2">Щось пішло не так</h1>
          <p className="text-text-secondary text-sm mb-6">
            {this.state.error?.message ?? 'Невідома помилка'}
          </p>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="px-5 py-2.5 bg-accent-cyan text-bg-primary font-semibold rounded-xl text-sm"
          >
            Перезавантажити
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

import React, { Component } from 'react';
import { AlertTriangle, ArrowLeft, RotateCcw } from 'lucide-react';

export default class AnalysisErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('AnalysisErrorBoundary caught rendering error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onRetry) {
      this.props.onRetry();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="bg-white border border-line p-10 sm:p-14 text-center shadow-subtle space-y-5 max-w-xl mx-auto my-8">
          <div className="w-12 h-12 rounded-full bg-legalamber/10 border border-legalamber/30 flex items-center justify-center mx-auto">
            <AlertTriangle className="w-6 h-6 text-crimson" />
          </div>
          <div className="space-y-1.5">
            <h2 className="text-xl font-bold font-sans text-midnight tracking-tight">
              Unable to display this analysis
            </h2>
            <p className="text-[13px] text-charcoal-muted leading-relaxed">
              The analysis data could not be rendered. Please return to Workspace and try again.
            </p>
          </div>

          <div className="flex items-center justify-center space-x-3 pt-3">
            {this.props.onBackToWorkspace && (
              <button
                onClick={this.props.onBackToWorkspace}
                className="btn-secondary py-2 px-4 text-[13px] inline-flex items-center space-x-2"
              >
                <ArrowLeft className="w-4 h-4 text-midnight" />
                <span>Back to Workspace</span>
              </button>
            )}
            <button
              onClick={this.handleReset}
              className="btn-primary py-2 px-4 text-[13px] inline-flex items-center space-x-2"
            >
              <RotateCcw className="w-4 h-4 text-gold-light" />
              <span>Retry / Open Again</span>
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

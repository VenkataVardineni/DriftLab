"""Command-line interface for DriftLab."""

import argparse
from pathlib import Path
import sys


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="DriftLab - ML monitoring toolkit")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run drift analysis')
    run_parser.add_argument('--ref', help='Reference dataset path (overrides config)')
    run_parser.add_argument('--cur', help='Current dataset path (overrides config)')
    run_parser.add_argument('--out', help='Output directory (overrides config)')
    run_parser.add_argument('--config', help='Config file path (YAML)')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate synthetic drift data')
    gen_parser.add_argument('--output-dir', default='data', help='Output directory')
    gen_parser.add_argument('--n-samples', type=int, default=1000, help='Number of samples')
    gen_parser.add_argument('--seed', type=int, default=42, help='Random seed')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        from driftlab.run import run_drift_analysis
        
        # Load config if provided
        config = {}
        if args.config:
            import yaml
            with open(args.config, 'r') as f:
                config = yaml.safe_load(f)
        
        # Get paths from args or config
        ref_path = args.ref or config.get('input', {}).get('reference')
        cur_path = args.cur or config.get('input', {}).get('current')
        output_dir = args.out or config.get('output', {}).get('directory', 'reports/run_001')
        
        if not ref_path or not cur_path:
            parser.error("--ref and --cur are required, or provide --config with input paths")
        
        run_drift_analysis(
            ref_path=ref_path,
            cur_path=cur_path,
            output_dir=output_dir,
            config_path=args.config
        )
    elif args.command == 'generate':
        import sys
        from pathlib import Path
        # Add project root to path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        from data.synthetic.generate import generate_demo_data
        generate_demo_data(args.output_dir, args.n_samples, args.seed)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()


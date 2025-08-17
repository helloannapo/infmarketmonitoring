#!/bin/bash
# Infineon Competitive Intelligence Scheduler Runner
# Makes it easy to run the scheduler with common configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Infineon Competitive Intelligence Scheduler"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  daily      Run every 24 hours (default)"
    echo "  twice      Run every 12 hours"
    echo "  hourly     Run every hour"
    echo "  custom N   Run every N hours"
    echo "  once       Run once and exit"
    echo "  test       Test the scheduler (run once with verbose output)"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 daily          # Run every 24 hours"
    echo "  $0 twice          # Run every 12 hours"
    echo "  $0 custom 6       # Run every 6 hours"
    echo "  $0 once           # Run once and exit"
    echo "  $0 test           # Test run with verbose output"
    echo ""
}

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found!"
        print_info "Please run setup_venv.sh first to create the virtual environment"
        exit 1
    fi
}

# Function to activate virtual environment
activate_venv() {
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    else
        print_error "Could not find virtual environment activation script"
        exit 1
    fi
}

# Function to check if scheduler script exists
check_scheduler() {
    if [ ! -f "scheduled_intelligence.py" ]; then
        print_error "Scheduler script not found!"
        print_info "Make sure scheduled_intelligence.py exists in the current directory"
        exit 1
    fi
}

# Function to run the scheduler
run_scheduler() {
    local interval=$1
    local once=$2
    local verbose=$3
    
    local cmd="python scheduled_intelligence.py"
    
    if [ "$once" = "true" ]; then
        cmd="$cmd --once"
    else
        cmd="$cmd --interval $interval"
    fi
    
    if [ "$verbose" = "true" ]; then
        cmd="$cmd --verbose"
    fi
    
    print_info "Running scheduler: $cmd"
    print_info "Press Ctrl+C to stop the scheduler"
    echo ""
    
    eval $cmd
}

# Main script logic
main() {
    print_info "Infineon Competitive Intelligence Scheduler"
    print_info "=========================================="
    
    # Check if virtual environment exists
    check_venv
    
    # Check if scheduler script exists
    check_scheduler
    
    # Activate virtual environment
    activate_venv
    
    # Parse arguments
    case "${1:-daily}" in
        "daily")
            print_info "Starting daily scheduler (every 24 hours)"
            run_scheduler 24 false false
            ;;
        "twice")
            print_info "Starting twice-daily scheduler (every 12 hours)"
            run_scheduler 12 false false
            ;;
        "hourly")
            print_info "Starting hourly scheduler (every 1 hour)"
            run_scheduler 1 false false
            ;;
        "custom")
            if [ -z "$2" ]; then
                print_error "Please specify the interval in hours"
                echo "Usage: $0 custom N"
                exit 1
            fi
            print_info "Starting custom scheduler (every $2 hours)"
            run_scheduler "$2" false false
            ;;
        "once")
            print_info "Running intelligence job once"
            run_scheduler 24 true false
            ;;
        "test")
            print_info "Running test (once with verbose output)"
            run_scheduler 24 true true
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"

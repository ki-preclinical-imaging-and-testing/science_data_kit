#!/usr/bin/env python
"""
Performance benchmarking script for the Flask application.

This script measures page load times and API response times for the Flask application,
and compares them with the Streamlit version if available.
"""

import os
import sys
import time
import json
import requests
import statistics
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Constants
DEFAULT_FLASK_URL = "http://localhost:5000"
DEFAULT_STREAMLIT_URL = "http://localhost:8501"
DEFAULT_NUM_RUNS = 10
DEFAULT_OUTPUT_DIR = "benchmark_results"


class PerformanceBenchmark:
    """Class for benchmarking the Flask application."""

    def __init__(
        self,
        flask_url: str = DEFAULT_FLASK_URL,
        streamlit_url: Optional[str] = DEFAULT_STREAMLIT_URL,
        num_runs: int = DEFAULT_NUM_RUNS,
        output_dir: str = DEFAULT_OUTPUT_DIR,
    ):
        """Initialize the benchmark.

        Args:
            flask_url: URL of the Flask application
            streamlit_url: URL of the Streamlit application (optional)
            num_runs: Number of runs for each test
            output_dir: Directory to save benchmark results
        """
        self.flask_url = flask_url
        self.streamlit_url = streamlit_url
        self.num_runs = num_runs
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize results dictionary
        self.results = {
            "flask": {
                "page_load_times": {},
                "api_response_times": {},
            },
            "streamlit": {
                "page_load_times": {},
                "api_response_times": {},
            } if streamlit_url else None,
        }
        
        # Session for making requests
        self.flask_session = requests.Session()
        self.streamlit_session = requests.Session() if streamlit_url else None

    def measure_page_load_time(self, url: str, session: requests.Session) -> float:
        """Measure the time it takes to load a page.

        Args:
            url: URL of the page to load
            session: Session to use for making the request

        Returns:
            Time in seconds it took to load the page
        """
        start_time = time.time()
        response = session.get(url)
        end_time = time.time()
        
        # Ensure the request was successful
        response.raise_for_status()
        
        return end_time - start_time

    def measure_api_response_time(
        self,
        url: str,
        session: requests.Session,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Measure the time it takes for an API endpoint to respond.

        Args:
            url: URL of the API endpoint
            session: Session to use for making the request
            method: HTTP method to use (GET, POST, etc.)
            data: Form data to send with the request
            json_data: JSON data to send with the request

        Returns:
            Time in seconds it took for the API to respond
        """
        start_time = time.time()
        
        if method.upper() == "GET":
            response = session.get(url)
        elif method.upper() == "POST":
            response = session.post(url, data=data, json=json_data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        end_time = time.time()
        
        # Ensure the request was successful
        response.raise_for_status()
        
        return end_time - start_time

    def benchmark_flask_pages(self):
        """Benchmark page load times for the Flask application."""
        pages = [
            ("Home", ""),
            ("Connect", "connect"),
            ("Dashboard", "dashboard"),
            ("File Explorer", "file-explorer"),
            ("Explore", "explore"),
            ("About", "about"),
            ("Preferences", "preferences"),
        ]
        
        for page_name, page_path in pages:
            url = f"{self.flask_url}/{page_path}"
            times = []
            
            print(f"Benchmarking Flask page: {page_name}")
            
            for i in range(self.num_runs):
                try:
                    time_taken = self.measure_page_load_time(url, self.flask_session)
                    times.append(time_taken)
                    print(f"  Run {i+1}/{self.num_runs}: {time_taken:.4f} seconds")
                except Exception as e:
                    print(f"  Error on run {i+1}: {str(e)}")
            
            if times:
                self.results["flask"]["page_load_times"][page_name] = {
                    "mean": statistics.mean(times),
                    "median": statistics.median(times),
                    "min": min(times),
                    "max": max(times),
                    "stdev": statistics.stdev(times) if len(times) > 1 else 0,
                    "raw": times,
                }

    def benchmark_flask_apis(self):
        """Benchmark API response times for the Flask application."""
        apis = [
            ("Get Available Connections", "GET", "api/connect/available", None, None),
            ("Get Active Connections", "GET", "api/connect/active", None, None),
            ("Get Directory Contents", "GET", "api/file-explorer/list?path=/tmp", None, None),
            ("Get Dashboard Data", "GET", "api/dashboard/data", None, None),
        ]
        
        for api_name, method, path, data, json_data in apis:
            url = f"{self.flask_url}/{path}"
            times = []
            
            print(f"Benchmarking Flask API: {api_name}")
            
            for i in range(self.num_runs):
                try:
                    time_taken = self.measure_api_response_time(url, self.flask_session, method, data, json_data)
                    times.append(time_taken)
                    print(f"  Run {i+1}/{self.num_runs}: {time_taken:.4f} seconds")
                except Exception as e:
                    print(f"  Error on run {i+1}: {str(e)}")
            
            if times:
                self.results["flask"]["api_response_times"][api_name] = {
                    "mean": statistics.mean(times),
                    "median": statistics.median(times),
                    "min": min(times),
                    "max": max(times),
                    "stdev": statistics.stdev(times) if len(times) > 1 else 0,
                    "raw": times,
                }

    def benchmark_streamlit_pages(self):
        """Benchmark page load times for the Streamlit application."""
        if not self.streamlit_url:
            print("Streamlit URL not provided, skipping Streamlit benchmarks")
            return
        
        pages = [
            ("Home", ""),
            ("Connect", "connect"),
            ("Dashboard", "dashboard"),
            ("File Browser", "file_browser"),
            ("Explore", "explore"),
            ("About", "about"),
            ("Preferences", "preferences"),
        ]
        
        for page_name, page_path in pages:
            url = f"{self.streamlit_url}/{page_path}"
            times = []
            
            print(f"Benchmarking Streamlit page: {page_name}")
            
            for i in range(self.num_runs):
                try:
                    time_taken = self.measure_page_load_time(url, self.streamlit_session)
                    times.append(time_taken)
                    print(f"  Run {i+1}/{self.num_runs}: {time_taken:.4f} seconds")
                except Exception as e:
                    print(f"  Error on run {i+1}: {str(e)}")
            
            if times:
                self.results["streamlit"]["page_load_times"][page_name] = {
                    "mean": statistics.mean(times),
                    "median": statistics.median(times),
                    "min": min(times),
                    "max": max(times),
                    "stdev": statistics.stdev(times) if len(times) > 1 else 0,
                    "raw": times,
                }

    def run_benchmarks(self):
        """Run all benchmarks."""
        print("Starting benchmarks...")
        
        # Benchmark Flask pages
        self.benchmark_flask_pages()
        
        # Benchmark Flask APIs
        self.benchmark_flask_apis()
        
        # Benchmark Streamlit pages if URL provided
        if self.streamlit_url:
            self.benchmark_streamlit_pages()
        
        print("Benchmarks completed")

    def save_results(self):
        """Save benchmark results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save raw results as JSON
        json_path = os.path.join(self.output_dir, f"benchmark_results_{timestamp}.json")
        with open(json_path, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Raw results saved to {json_path}")
        
        # Create summary DataFrame for page load times
        page_load_data = []
        
        for page_name in self.results["flask"]["page_load_times"]:
            flask_data = self.results["flask"]["page_load_times"][page_name]
            streamlit_data = None
            
            if self.streamlit_url and self.results["streamlit"] and page_name in self.results["streamlit"]["page_load_times"]:
                streamlit_data = self.results["streamlit"]["page_load_times"][page_name]
            
            row = {
                "Page": page_name,
                "Flask Mean (s)": flask_data["mean"],
                "Flask Median (s)": flask_data["median"],
                "Flask Min (s)": flask_data["min"],
                "Flask Max (s)": flask_data["max"],
                "Flask StdDev (s)": flask_data["stdev"],
            }
            
            if streamlit_data:
                row.update({
                    "Streamlit Mean (s)": streamlit_data["mean"],
                    "Streamlit Median (s)": streamlit_data["median"],
                    "Streamlit Min (s)": streamlit_data["min"],
                    "Streamlit Max (s)": streamlit_data["max"],
                    "Streamlit StdDev (s)": streamlit_data["stdev"],
                    "Improvement (%)": ((streamlit_data["mean"] - flask_data["mean"]) / streamlit_data["mean"]) * 100,
                })
            
            page_load_data.append(row)
        
        if page_load_data:
            page_load_df = pd.DataFrame(page_load_data)
            page_load_csv = os.path.join(self.output_dir, f"page_load_times_{timestamp}.csv")
            page_load_df.to_csv(page_load_csv, index=False)
            print(f"Page load time summary saved to {page_load_csv}")
            
            # Create bar chart for page load times
            self.create_page_load_chart(page_load_df, timestamp)
        
        # Create summary DataFrame for API response times
        api_data = []
        
        for api_name in self.results["flask"]["api_response_times"]:
            flask_data = self.results["flask"]["api_response_times"][api_name]
            
            row = {
                "API": api_name,
                "Mean (s)": flask_data["mean"],
                "Median (s)": flask_data["median"],
                "Min (s)": flask_data["min"],
                "Max (s)": flask_data["max"],
                "StdDev (s)": flask_data["stdev"],
            }
            
            api_data.append(row)
        
        if api_data:
            api_df = pd.DataFrame(api_data)
            api_csv = os.path.join(self.output_dir, f"api_response_times_{timestamp}.csv")
            api_df.to_csv(api_csv, index=False)
            print(f"API response time summary saved to {api_csv}")
            
            # Create bar chart for API response times
            self.create_api_response_chart(api_df, timestamp)

    def create_page_load_chart(self, df: pd.DataFrame, timestamp: str):
        """Create a bar chart comparing page load times.

        Args:
            df: DataFrame containing page load time data
            timestamp: Timestamp for the filename
        """
        plt.figure(figsize=(12, 8))
        
        if "Streamlit Mean (s)" in df.columns:
            # Create grouped bar chart comparing Flask and Streamlit
            bar_width = 0.35
            index = range(len(df))
            
            plt.bar([i - bar_width/2 for i in index], df["Flask Mean (s)"], bar_width, label="Flask")
            plt.bar([i + bar_width/2 for i in index], df["Streamlit Mean (s)"], bar_width, label="Streamlit")
            
            plt.xlabel("Page")
            plt.ylabel("Mean Load Time (seconds)")
            plt.title("Flask vs Streamlit Page Load Times")
            plt.xticks(index, df["Page"])
            plt.legend()
            
            # Add improvement percentages as text
            for i, row in enumerate(df.itertuples()):
                if hasattr(row, "Improvement____"):
                    plt.text(i, max(row._2, row._7) + 0.05, f"{row._12:.1f}%", ha="center")
        else:
            # Create simple bar chart for Flask only
            plt.bar(df["Page"], df["Flask Mean (s)"])
            plt.xlabel("Page")
            plt.ylabel("Mean Load Time (seconds)")
            plt.title("Flask Page Load Times")
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"page_load_times_{timestamp}.png"))
        plt.close()

    def create_api_response_chart(self, df: pd.DataFrame, timestamp: str):
        """Create a bar chart showing API response times.

        Args:
            df: DataFrame containing API response time data
            timestamp: Timestamp for the filename
        """
        plt.figure(figsize=(12, 8))
        
        plt.bar(df["API"], df["Mean (s)"])
        plt.xlabel("API")
        plt.ylabel("Mean Response Time (seconds)")
        plt.title("Flask API Response Times")
        plt.xticks(rotation=45, ha="right")
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"api_response_times_{timestamp}.png"))
        plt.close()


def main():
    """Main function to run the benchmark script."""
    parser = argparse.ArgumentParser(description="Benchmark the Flask application")
    parser.add_argument("--flask-url", default=DEFAULT_FLASK_URL, help="URL of the Flask application")
    parser.add_argument("--streamlit-url", default=DEFAULT_STREAMLIT_URL, help="URL of the Streamlit application (optional)")
    parser.add_argument("--no-streamlit", action="store_true", help="Skip Streamlit benchmarks")
    parser.add_argument("--runs", type=int, default=DEFAULT_NUM_RUNS, help="Number of runs for each test")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Directory to save benchmark results")
    
    args = parser.parse_args()
    
    streamlit_url = None if args.no_streamlit else args.streamlit_url
    
    benchmark = PerformanceBenchmark(
        flask_url=args.flask_url,
        streamlit_url=streamlit_url,
        num_runs=args.runs,
        output_dir=args.output_dir,
    )
    
    benchmark.run_benchmarks()
    benchmark.save_results()


if __name__ == "__main__":
    main()
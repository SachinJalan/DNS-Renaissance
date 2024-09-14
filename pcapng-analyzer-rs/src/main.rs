use csv::Writer;
use pcap::{Capture, Packet};
use std::collections::HashMap;
use std::env;
use std::fs::File;

#[derive(Debug)]
struct Result {
    domain: String,
    total_packets: u32,
    total_bytes: u32,
    total_dns_packets: u32,
    total_dns_bytes: u32,
    total_time: u64,
    total_dns_time: u64,
    ttfb: u64,
}

fn analyze_packets(packets: Vec<Packet>) -> HashMap<String, Result> {
    let mut results: HashMap<String, Result> = HashMap::new();

    for packet in packets {
        // Assuming DNS packet
        let domain = "example.com".to_string(); // Placeholder for actual DNS extraction
        let result = results.entry(domain.clone()).or_insert(Result {
            domain,
            total_packets: 0,
            total_bytes: 0,
            total_dns_packets: 0,
            total_dns_bytes: 0,
            total_time: 0,
            total_dns_time: 0,
            ttfb: 0,
        });

        // Placeholder for packet parsing logic
        result.total_packets += 1;
        result.total_bytes += packet.len() as u32;
        result.total_dns_packets += 1;
        result.total_dns_bytes += packet.len() as u32;
    }

    results
}

fn save_results_to_csv(results: HashMap<String, Result>, filename: &str) {
    let file = File::create(filename).expect("Could not create CSV file");
    let mut writer = Writer::from_writer(file);

    writer
        .write_record(&[
            "Domain",
            "TotalPackets",
            "TotalBytes",
            "TotalDNSPackets",
            "TotalDNSBytes",
            "TotalTime",
            "TotalDNSTime",
            "TTFB",
        ])
        .unwrap();

    for result in results.values() {
        writer
            .write_record(&[
                &result.domain,
                &result.total_packets.to_string(),
                &result.total_bytes.to_string(),
                &result.total_dns_packets.to_string(),
                &result.total_dns_bytes.to_string(),
                &result.total_time.to_string(),
                &result.total_dns_time.to_string(),
                &result.ttfb.to_string(),
            ])
            .unwrap();
    }

    writer.flush().unwrap();
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: cargo run <pcapng_file>");
        return;
    }

    let pcapng_file = &args[1];

    let mut cap = Capture::from_file(pcapng_file).expect("Error opening file");

    // let mut packets: Vec<Packet> = Vec::new();

    // while let Ok(packet) = cap.next_packet() {
    //     println!("{:?}", packet.data);
    // }

    // let results = analyze_packets(packets);

    // let output_file = "results.csv";
    // save_results_to_csv(results, output_file);

    // println!("Results saved in {}", output_file);
}

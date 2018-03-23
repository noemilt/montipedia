from scraper import MontipediaScraper

output_file = "dataset.csv"

scraper = MontipediaScraper();
scraper.scrape();
#scraper.data2csv(output_file);

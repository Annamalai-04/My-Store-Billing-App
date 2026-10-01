package com.example.demo.service;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.List;
import java.util.Optional;

import org.springframework.stereotype.Service;

import com.example.demo.dto.ProductRequest;
import com.example.demo.dto.ScanProductResponse;
import com.example.demo.model.Product;
import com.example.demo.repository.ProductRepository;

@Service
public class ProductService {

    private final ProductRepository productRepository;

    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public List<Product> all() {
        return productRepository.findAll();
    }

    // Search ONLY the local MySQL products table.
    // Searches by product name OR barcode.
    public List<Product> search(String search) {
        if (search == null || search.isBlank()) {
            return productRepository.findAll();
        }

        String text = search.trim().toLowerCase();

        return productRepository.findAll()
                .stream()
                .filter(product -> {
                    boolean nameMatches =
                            product.getName() != null
                                    && product.getName().toLowerCase().contains(text);

                    boolean barcodeMatches =
                            product.getBarcode() != null
                                    && product.getBarcode().toLowerCase().contains(text);

                    return nameMatches || barcodeMatches;
                })
                .toList();
    }

    public Product create(ProductRequest request) {

        Product product = new Product();

        product.setName(request.getName());
        product.setGroupName(request.getGroupName());
        product.setBarcode(request.getBarcode());

        product.setPrice(
                request.getPrice() == null
                        ? 0.0
                        : request.getPrice()
        );

        product.setDiscount(
                request.getDiscount() == null
                        ? 0.0
                        : request.getDiscount()
        );

        product.setStock(
                request.getStock() == null
                        ? 0
                        : request.getStock()
        );

        // Invalid/blank expiry becomes NULL.
        product.setExpiryDate(
                parseExpiryDate(request.getExpiryDate())
        );

        return productRepository.save(product);
    }

    public Product update(Long id, ProductRequest request) {

        Product product = productRepository.findById(id)
                .orElseThrow(() ->
                        new RuntimeException(
                                "Product not found: " + id
                        )
                );

        product.setName(request.getName());
        product.setGroupName(request.getGroupName());
        product.setBarcode(request.getBarcode());

        product.setPrice(
                request.getPrice() == null
                        ? 0.0
                        : request.getPrice()
        );

        product.setDiscount(
                request.getDiscount() == null
                        ? 0.0
                        : request.getDiscount()
        );

        product.setStock(
                request.getStock() == null
                        ? 0
                        : request.getStock()
        );

        // Invalid/blank expiry becomes NULL.
        product.setExpiryDate(
                parseExpiryDate(request.getExpiryDate())
        );

        return productRepository.save(product);
    }

    public Product addStock(Long id, int quantity) {

        if (quantity <= 0) {
            throw new RuntimeException("Stock quantity must be greater than 0");
        }

        Product product = productRepository.findById(id)
                .orElseThrow(() ->
                        new RuntimeException("Product not found: " + id)
                );

        int currentStock = product.getStock();

        product.setStock(currentStock + quantity);

        return productRepository.save(product);
    }
    
    
    public void delete(Long id) {
        if (!productRepository.existsById(id)) {
            throw new RuntimeException("Product not found: " + id);
        }

        productRepository.deleteById(id);
    }

    // Barcode scan uses ONLY local MySQL.
    // No Open Food Facts, UPCitemdb, Barcode Lookup, etc.
    public ScanProductResponse scan(String barcode) {
        return scanBarcode(barcode);
    }

    public ScanProductResponse scanBarcode(String barcode) {

        if (barcode == null || barcode.trim().isEmpty()) {
            return notFoundResponse(barcode, "Product not found.");
        }

        String cleanBarcode = barcode.trim();

        Optional<Product> localProduct =
                productRepository.findByBarcode(cleanBarcode);

        if (localProduct.isPresent()) {
            Product product = localProduct.get();

            System.out.println(
                    "Product found in local MySQL: " + product.getName());

            return localProductResponse(product, cleanBarcode);
        }

        System.out.println(
                "Product not found for barcode: " + cleanBarcode);

        return notFoundResponse(
                cleanBarcode,
                "Product not found.");
    }

    private ScanProductResponse localProductResponse(
            Product product,
            String barcode) {

        ScanProductResponse response = new ScanProductResponse();

        response.setBarcode(barcode);
        response.setFound(true);
        response.setProductId(product.getProductId());
        response.setName(product.getName());
        response.setGroupName(product.getGroupName());
        response.setPrice(product.getPrice());
        response.setStock(product.getStock());

        response.setExpiryDate(
                product.getExpiryDate() == null
                        ? null
                        : product.getExpiryDate().toString());

        response.setImageUrl(null);
        response.setBrand(null);
        response.setQuantity(null);
        response.setSource("MYSTOREAPP");
        response.setMessage("Product found in local database.");

        return response;
    }

    private ScanProductResponse notFoundResponse(
            String barcode,
            String message) {

        ScanProductResponse response = new ScanProductResponse();

        response.setBarcode(barcode);
        response.setFound(false);
        response.setProductId(null);
        response.setName(null);
        response.setBrand(null);
        response.setQuantity(null);
        response.setGroupName(null);
        response.setPrice(null);
        response.setStock(null);
        response.setExpiryDate(null);
        response.setImageUrl(null);
        response.setSource("NONE");
        response.setMessage(message);

        return response;
    }
    
    private LocalDate parseExpiryDate(String value) {

        if (value == null || value.isBlank()) {
            return null;
        }

        try {

            return LocalDate.parse(
                    value.trim(),
                    DateTimeFormatter.ISO_LOCAL_DATE
            );

        } catch (DateTimeParseException e) {

            // Any invalid text becomes NULL.
            return null;
        }
    }
}

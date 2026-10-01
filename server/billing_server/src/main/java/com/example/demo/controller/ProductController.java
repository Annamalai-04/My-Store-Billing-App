package com.example.demo.controller;

import com.example.demo.dto.ProductRequest;
import com.example.demo.service.ProductService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    @GetMapping
    public Object all(@RequestParam(required = false) String search) {
        if (search == null || search.isBlank()) {
            return productService.all();
        }

        return productService.search(search);
    }

    @PostMapping
    public Object create(@RequestBody ProductRequest request) {
        return productService.create(request);
    }

    @PutMapping("/{id}")
    public Object update(
            @PathVariable Long id,
            @RequestBody ProductRequest request) {

        return productService.update(id, request);
    }

    @PatchMapping("/{id}/add-stock")
    public Object addStock(
            @PathVariable Long id,
            @RequestBody Map<String, Integer> request) {

        Integer quantity = request.get("quantity");

        if (quantity == null || quantity <= 0) {
            throw new RuntimeException(
                    "Stock quantity to add must be greater than 0."
            );
        }

        return productService.addStock(id, quantity);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        productService.delete(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/scan/{barcode}")
    public Object scan(@PathVariable String barcode) {
        return productService.scan(barcode);
    }
}

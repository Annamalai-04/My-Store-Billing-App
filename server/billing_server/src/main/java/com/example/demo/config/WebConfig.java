package com.example.demo.config;

import org.springframework.context.annotation.*;
import org.springframework.web.servlet.config.annotation.*;

@Configuration
public class WebConfig implements WebMvcConfigurer {
	public void addCorsMappings(CorsRegistry r) {
		r.addMapping("/api/**").allowedOrigins("*").allowedMethods("*").allowedHeaders("*");
	}
}
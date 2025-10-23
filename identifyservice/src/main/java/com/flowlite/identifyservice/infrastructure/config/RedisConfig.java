package com.flowlite.identifyservice.infrastructure.config;

import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.StringRedisSerializer;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;

/**
 * Configuración de Redis para el blacklist de tokens JWT.
 * 
 * Esta configuración establece:
 * - Serialización de claves y valores como String
 * - Configuración de RedisTemplate para operaciones con tokens
 * - Habilitación de cache para optimización de rendimiento
 */
@Configuration
@EnableCaching
public class RedisConfig {
    
    /**
     * Configura RedisTemplate para operaciones con tokens revocados.
     * 
     * @param connectionFactory Factory de conexión a Redis
     * @return RedisTemplate configurado para strings
     */
    @Bean
    public RedisTemplate<String, String> redisTemplate(RedisConnectionFactory connectionFactory) {
        RedisTemplate<String, String> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);
        
        // Serialización de claves y valores como String
        template.setKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(new StringRedisSerializer());
        template.setHashKeySerializer(new StringRedisSerializer());
        template.setHashValueSerializer(new StringRedisSerializer());
        
        // Habilitar transacciones
        template.setEnableTransactionSupport(true);
        
        return template;
    }
    
    /**
     * Configura RedisTemplate adicional para operaciones con objetos complejos.
     * Necesario para PendingUserRedisRepository que maneja objetos PendingUserData.
     * 
     * @param connectionFactory Factory de conexión a Redis
     * @return RedisTemplate configurado para objetos complejos
     */
    @Bean
    public RedisTemplate<String, Object> redisObjectTemplate(RedisConnectionFactory connectionFactory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);
        
        // Serialización de claves como String, valores como JSON
        template.setKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(new GenericJackson2JsonRedisSerializer());
        template.setHashKeySerializer(new StringRedisSerializer());
        template.setHashValueSerializer(new GenericJackson2JsonRedisSerializer());
        
        // Habilitar transacciones
        template.setEnableTransactionSupport(true);
        
        return template;
    }
}

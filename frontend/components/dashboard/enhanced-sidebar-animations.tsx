import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';

interface EnhancedSidebarAnimationsProps {
  isExpanded: boolean;
  isPinned: boolean;
  navigationItems: any[];
}

export function EnhancedSidebarAnimations({ 
  isExpanded, 
  isPinned, 
  navigationItems 
}: EnhancedSidebarAnimationsProps) {
  const animationRef = useRef<gsap.core.Timeline | null>(null);
  const prevExpandedRef = useRef(isExpanded);

  useEffect(() => {
    const wasExpanded = prevExpandedRef.current;
    const isNowExpanded = isExpanded || isPinned;
    
    // Only animate if expansion state changed
    if (wasExpanded !== isNowExpanded) {
      // Kill any running animations
      if (animationRef.current) {
        animationRef.current.kill();
      }

      if (isNowExpanded) {
        // Expanding animation
        animateExpansion();
      } else {
        // Collapsing animation
        animateCollapse();
      }
    }

    prevExpandedRef.current = isNowExpanded;
  }, [isExpanded, isPinned]);

  const animateExpansion = () => {
    const sidebar = document.querySelector('[data-sidebar-main]');
    const navItems = document.querySelectorAll('[data-nav-item]');
    const navTexts = document.querySelectorAll('[data-nav-text]');
    const logo = document.querySelector('[data-sidebar-logo]');
    const userSection = document.querySelector('[data-user-section]');

    if (!sidebar) return;

    const tl = gsap.timeline();
    animationRef.current = tl;

    // Create staggered background layers effect
    const backgroundLayers = createBackgroundLayers();
    
    // Animate background layers first
    backgroundLayers.forEach((layer, index) => {
      tl.fromTo(layer, 
        { xPercent: -100 }, 
        { 
          xPercent: 0, 
          duration: 0.5, 
          ease: 'power4.out' 
        }, 
        index * 0.07
      );
    });

    // Animate navigation items with stagger
    if (navItems.length) {
      tl.fromTo(navItems,
        { x: -20, opacity: 0 },
        {
          x: 0,
          opacity: 1,
          duration: 0.6,
          ease: 'power3.out',
          stagger: {
            each: 0.1,
            from: 'start'
          }
        },
        0.3
      );
    }

    // Animate text elements
    if (navTexts.length) {
      tl.fromTo(navTexts,
        { x: -15, opacity: 0 },
        {
          x: 0,
          opacity: 1,
          duration: 0.4,
          ease: 'power2.out',
          stagger: 0.05
        },
        0.4
      );
    }

    // Animate logo
    if (logo) {
      tl.fromTo(logo,
        { scale: 0.8, opacity: 0 },
        {
          scale: 1,
          opacity: 1,
          duration: 0.5,
          ease: 'back.out(1.7)'
        },
        0.2
      );
    }

    // Animate user section
    if (userSection) {
      tl.fromTo(userSection,
        { y: 20, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.4,
          ease: 'power2.out'
        },
        0.6
      );
    }

    // Clean up background layers after animation
    tl.call(() => {
      backgroundLayers.forEach(layer => {
        layer.remove();
      });
    });
  };

  const animateCollapse = () => {
    const navTexts = document.querySelectorAll('[data-nav-text]');
    const logo = document.querySelector('[data-sidebar-logo]');
    const userSection = document.querySelector('[data-user-section]');

    const tl = gsap.timeline();
    animationRef.current = tl;

    // Animate out text elements
    if (navTexts.length) {
      tl.to(navTexts, {
        x: -10,
        opacity: 0,
        duration: 0.3,
        ease: 'power2.in',
        stagger: 0.03
      });
    }

    // Animate out logo
    if (logo) {
      tl.to(logo, {
        scale: 0.8,
        opacity: 0,
        duration: 0.3,
        ease: 'power2.in'
      }, 0);
    }

    // Animate out user section
    if (userSection) {
      tl.to(userSection, {
        y: 10,
        opacity: 0,
        duration: 0.3,
        ease: 'power2.in'
      }, 0);
    }
  };

  const createBackgroundLayers = () => {
    const sidebar = document.querySelector('[data-sidebar-main]');
    if (!sidebar) return [];

    const colors = ['#0f172a', '#1e293b', '#334155'];
    const layers: HTMLElement[] = [];

    colors.forEach((color, index) => {
      const layer = document.createElement('div');
      layer.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: ${color};
        z-index: -${index + 1};
        transform: translateX(-100%);
      `;
      sidebar.appendChild(layer);
      layers.push(layer);
    });

    return layers;
  };

  // Add icon rotation animation
  useEffect(() => {
    const icons = document.querySelectorAll('[data-nav-icon]');
    
    icons.forEach((icon) => {
      const element = icon as HTMLElement;
      
      element.addEventListener('mouseenter', () => {
        gsap.to(icon, {
          rotation: 360,
          duration: 0.6,
          ease: 'power2.out'
        });
      });

      element.addEventListener('mouseleave', () => {
        gsap.to(icon, {
          rotation: 0,
          duration: 0.4,
          ease: 'power2.out'
        });
      });
    });

    return () => {
      icons.forEach((icon) => {
        const element = icon as HTMLElement;
        element.removeEventListener('mouseenter', () => {});
        element.removeEventListener('mouseleave', () => {});
      });
    };
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationRef.current) {
        animationRef.current.kill();
      }
    };
  }, []);

  return null; // This component only provides animation logic
}
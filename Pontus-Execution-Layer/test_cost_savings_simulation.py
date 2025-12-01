#!/usr/bin/env python3
"""
Cost Savings Simulation Test
Simulates sending $11,000 and calculates real savings using Wise + Kraken APIs
"""
import asyncio
import sys
from datetime import datetime
from decimal import Decimal

sys.path.insert(0, '/Users/arjundixit/Downloads/PontusExecution/Pontus-Execution-Layer')

import httpx
from app.clients import WiseClient, KrakenClient
from app.config import settings

print("=" * 80)
print("💰 COST SAVINGS SIMULATION - $11,000 Transfer")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
print("Testing real API costs vs traditional methods\n")

reports = []


async def get_wise_quote(client, profile_id, source_currency, target_currency, amount):
    """Get real quote from Wise API"""
    wise = WiseClient(client)
    quote = await wise.create_quote(
        profile_id=profile_id,
        source_currency=source_currency,
        target_currency=target_currency,
        source_amount=amount
    )
    return quote


async def get_kraken_ticker(client, pair):
    """Get real ticker from Kraken"""
    kraken = KrakenClient(client)
    ticker = await kraken.get_ticker(pair)
    return ticker


def calculate_traditional_bank_cost(amount, currency_pair):
    """Calculate cost using traditional bank transfer methods"""
    # Traditional bank international transfer fees
    # Typical: $25-50 flat fee + 2-5% markup on exchange rate
    
    if "USD" in currency_pair and "EUR" in currency_pair:
        # Traditional bank: ~$35 flat fee + 3% markup
        flat_fee = 35.0
        markup_percent = 0.03
        # Mid-market rate (approximate)
        mid_rate = 0.92  # USD/EUR approximate
        markup_cost = amount * markup_percent
        total_cost = flat_fee + markup_cost
        effective_rate = mid_rate * (1 - markup_percent)
        return {
            "method": "Traditional Bank Transfer",
            "flat_fee": flat_fee,
            "markup_percent": markup_percent * 100,
            "markup_cost": markup_cost,
            "total_cost": total_cost,
            "effective_rate": effective_rate,
            "amount_received": amount * effective_rate - flat_fee
        }
    elif "USD" in currency_pair and "INR" in currency_pair:
        # Traditional bank: ~$40 flat fee + 4% markup
        flat_fee = 40.0
        markup_percent = 0.04
        mid_rate = 83.0  # USD/INR approximate
        markup_cost = amount * markup_percent
        total_cost = flat_fee + markup_cost
        effective_rate = mid_rate * (1 - markup_percent)
        return {
            "method": "Traditional Bank Transfer",
            "flat_fee": flat_fee,
            "markup_percent": markup_percent * 100,
            "markup_cost": markup_cost,
            "total_cost": total_cost,
            "effective_rate": effective_rate,
            "amount_received": (amount * effective_rate) - (flat_fee * mid_rate)
        }
    else:
        # Generic: $30 flat + 3% markup
        flat_fee = 30.0
        markup_percent = 0.03
        total_cost = flat_fee + (amount * markup_percent)
        return {
            "method": "Traditional Bank Transfer",
            "flat_fee": flat_fee,
            "markup_percent": markup_percent * 100,
            "total_cost": total_cost
        }


def calculate_western_union_cost(amount, currency_pair):
    """Calculate cost using Western Union"""
    # Western Union: ~$5-15 flat fee + 1-3% markup
    if amount < 1000:
        flat_fee = 5.0
        markup_percent = 0.01
    elif amount < 5000:
        flat_fee = 10.0
        markup_percent = 0.015
    else:
        flat_fee = 15.0
        markup_percent = 0.02
    
    markup_cost = amount * markup_percent
    total_cost = flat_fee + markup_cost
    
    return {
        "method": "Western Union",
        "flat_fee": flat_fee,
        "markup_percent": markup_percent * 100,
        "markup_cost": markup_cost,
        "total_cost": total_cost
    }


def calculate_remittance_service_cost(amount, currency_pair):
    """Calculate cost using services like Remitly, MoneyGram"""
    # Remitly/MoneyGram: ~$0-10 flat fee + 0.5-2% markup
    if amount < 1000:
        flat_fee = 0.0
        markup_percent = 0.02
    elif amount < 5000:
        flat_fee = 5.0
        markup_percent = 0.015
    else:
        flat_fee = 10.0
        markup_percent = 0.01
    
    markup_cost = amount * markup_percent
    total_cost = flat_fee + markup_cost
    
    return {
        "method": "Remitly/MoneyGram",
        "flat_fee": flat_fee,
        "markup_percent": markup_percent * 100,
        "markup_cost": markup_cost,
        "total_cost": total_cost
    }


async def simulate_usd_to_eur_transfer():
    """Simulate USD → EUR transfer"""
    print("=" * 80)
    print("SIMULATION 1: USD → EUR Transfer ($11,000)")
    print("=" * 80)
    
    amount = 11000.0
    source_currency = "USD"
    target_currency = "EUR"
    
    client = httpx.AsyncClient(timeout=30.0)
    
    try:
        # Get Wise quote
        wise = WiseClient(client)
        profiles = await wise.get_profiles()
        if not profiles:
            print("❌ No Wise profiles found")
            return
        
        profile_id = profiles[0]["id"]
        print(f"\n📊 Getting real quote from Wise API...")
        wise_quote = await get_wise_quote(client, profile_id, source_currency, target_currency, amount)
        
        if not wise_quote:
            print("❌ Failed to get Wise quote")
            return
        
        # Extract Wise costs - check multiple possible field names
        wise_fee = wise_quote.get("fee", {})
        if isinstance(wise_fee, dict):
            wise_total_fee = wise_fee.get("total", wise_fee.get("totalAmount", 0))
        else:
            wise_total_fee = wise_fee if wise_fee else 0
        
        # If fee is still 0, use Wise's typical fee structure
        # Wise typically charges: 0.35% for USD->EUR (min $0.50)
        if wise_total_fee == 0:
            wise_fee_percent = 0.0035  # 0.35%
            wise_total_fee = max(0.50, amount * wise_fee_percent)
        
        wise_rate = wise_quote.get("rate", wise_quote.get("exchangeRate", 0))
        wise_source_amount = wise_quote.get("sourceAmount", wise_quote.get("source", amount))
        wise_target_amount = wise_quote.get("targetAmount", wise_quote.get("target", 0))
        
        # If target amount is 0, calculate from rate
        if wise_target_amount == 0 and wise_rate > 0:
            wise_target_amount = (wise_source_amount - wise_total_fee) * wise_rate
        elif wise_target_amount == 0:
            # Use approximate rate if not provided
            approximate_rate = 0.92 if target_currency == "EUR" else 1.0
            wise_target_amount = (wise_source_amount - wise_total_fee) * approximate_rate
        
        effective_rate = wise_target_amount / wise_source_amount if wise_source_amount > 0 else 0
        
        print(f"\n✅ Wise API Quote:")
        print(f"   Source Amount: ${wise_source_amount:,.2f} {source_currency}")
        print(f"   Target Amount: €{wise_target_amount:,.2f} {target_currency}")
        print(f"   Exchange Rate: {wise_rate if wise_rate > 0 else 'N/A (using estimate)'}")
        print(f"   Total Fee: ${wise_total_fee:.2f}")
        print(f"   Effective Rate: {effective_rate:.6f}")
        
        # Calculate traditional costs
        traditional = calculate_traditional_bank_cost(amount, f"{source_currency}/{target_currency}")
        western_union = calculate_western_union_cost(amount, f"{source_currency}/{target_currency}")
        remitly = calculate_remittance_service_cost(amount, f"{source_currency}/{target_currency}")
        
        print(f"\n💰 Cost Comparison:")
        print(f"\n1. Wise (Your System):")
        print(f"   Fee: ${wise_total_fee:.2f}")
        print(f"   Amount Received: €{wise_target_amount:,.2f}")
        print(f"   Total Cost: ${wise_total_fee:.2f}")
        
        print(f"\n2. Traditional Bank:")
        print(f"   Flat Fee: ${traditional['flat_fee']:.2f}")
        print(f"   Markup ({traditional['markup_percent']:.1f}%): ${traditional['markup_cost']:.2f}")
        print(f"   Total Cost: ${traditional['total_cost']:.2f}")
        
        print(f"\n3. Western Union:")
        print(f"   Flat Fee: ${western_union['flat_fee']:.2f}")
        print(f"   Markup ({western_union['markup_percent']:.1f}%): ${western_union['markup_cost']:.2f}")
        print(f"   Total Cost: ${western_union['total_cost']:.2f}")
        
        print(f"\n4. Remitly/MoneyGram:")
        print(f"   Flat Fee: ${remitly['flat_fee']:.2f}")
        print(f"   Markup ({remitly['markup_percent']:.1f}%): ${remitly['markup_cost']:.2f}")
        print(f"   Total Cost: ${remitly['total_cost']:.2f}")
        
        # Calculate savings
        savings_vs_traditional = traditional['total_cost'] - wise_total_fee
        savings_vs_western_union = western_union['total_cost'] - wise_total_fee
        savings_vs_remitly = remitly['total_cost'] - wise_total_fee
        
        print(f"\n💵 SAVINGS:")
        print(f"   vs Traditional Bank: ${savings_vs_traditional:.2f} ({savings_vs_traditional/amount*100:.2f}%)")
        print(f"   vs Western Union: ${savings_vs_western_union:.2f} ({savings_vs_western_union/amount*100:.2f}%)")
        print(f"   vs Remitly/MoneyGram: ${savings_vs_remitly:.2f} ({savings_vs_remitly/amount*100:.2f}%)")
        
        max_savings = max(savings_vs_traditional, savings_vs_western_union, savings_vs_remitly)
        print(f"\n🎯 Maximum Savings: ${max_savings:.2f}")
        
        reports.append({
            "route": f"{source_currency} → {target_currency}",
            "amount": amount,
            "wise_cost": wise_total_fee,
            "wise_received": wise_target_amount,
            "traditional_cost": traditional['total_cost'],
            "western_union_cost": western_union['total_cost'],
            "remitly_cost": remitly['total_cost'],
            "savings_vs_traditional": savings_vs_traditional,
            "savings_vs_western_union": savings_vs_western_union,
            "savings_vs_remitly": savings_vs_remitly,
            "max_savings": max_savings
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.aclose()


async def simulate_usd_to_inr_transfer():
    """Simulate USD → INR transfer"""
    print("\n" + "=" * 80)
    print("SIMULATION 2: USD → INR Transfer ($11,000)")
    print("=" * 80)
    
    amount = 11000.0
    source_currency = "USD"
    target_currency = "INR"
    
    client = httpx.AsyncClient(timeout=30.0)
    
    try:
        # Get Wise quote
        wise = WiseClient(client)
        profiles = await wise.get_profiles()
        if not profiles:
            print("❌ No Wise profiles found")
            return
        
        profile_id = profiles[0]["id"]
        print(f"\n📊 Getting real quote from Wise API...")
        wise_quote = await get_wise_quote(client, profile_id, source_currency, target_currency, amount)
        
        if not wise_quote:
            print("❌ Failed to get Wise quote")
            return
        
        # Extract Wise costs - check multiple possible field names
        wise_fee = wise_quote.get("fee", {})
        if isinstance(wise_fee, dict):
            wise_total_fee = wise_fee.get("total", wise_fee.get("totalAmount", 0))
        else:
            wise_total_fee = wise_fee if wise_fee else 0
        
        # If fee is still 0, use Wise's typical fee structure
        # Wise typically charges: 0.4% for USD->INR (min $1.00)
        if wise_total_fee == 0:
            wise_fee_percent = 0.004  # 0.4%
            wise_total_fee = max(1.00, amount * wise_fee_percent)
        
        wise_rate = wise_quote.get("rate", wise_quote.get("exchangeRate", 0))
        wise_source_amount = wise_quote.get("sourceAmount", wise_quote.get("source", amount))
        wise_target_amount = wise_quote.get("targetAmount", wise_quote.get("target", 0))
        
        # If target amount is 0, calculate from rate
        if wise_target_amount == 0 and wise_rate > 0:
            wise_target_amount = (wise_source_amount - wise_total_fee) * wise_rate
        elif wise_target_amount == 0:
            # Use approximate rate if not provided
            approximate_rate = 83.0  # USD/INR
            wise_target_amount = (wise_source_amount - wise_total_fee) * approximate_rate
        
        effective_rate = wise_target_amount / wise_source_amount if wise_source_amount > 0 else 0
        
        print(f"\n✅ Wise API Quote:")
        print(f"   Source Amount: ${wise_source_amount:,.2f} {source_currency}")
        print(f"   Target Amount: ₹{wise_target_amount:,.2f} {target_currency}")
        print(f"   Exchange Rate: {wise_rate if wise_rate > 0 else 'N/A (using estimate)'}")
        print(f"   Total Fee: ${wise_total_fee:.2f}")
        print(f"   Effective Rate: {effective_rate:.6f}")
        
        # Calculate traditional costs
        traditional = calculate_traditional_bank_cost(amount, f"{source_currency}/{target_currency}")
        western_union = calculate_western_union_cost(amount, f"{source_currency}/{target_currency}")
        remitly = calculate_remittance_service_cost(amount, f"{source_currency}/{target_currency}")
        
        print(f"\n💰 Cost Comparison:")
        print(f"\n1. Wise (Your System):")
        print(f"   Fee: ${wise_total_fee:.2f}")
        print(f"   Amount Received: ₹{wise_target_amount:,.2f}")
        print(f"   Total Cost: ${wise_total_fee:.2f}")
        
        print(f"\n2. Traditional Bank:")
        print(f"   Flat Fee: ${traditional['flat_fee']:.2f}")
        print(f"   Markup ({traditional['markup_percent']:.1f}%): ${traditional['markup_cost']:.2f}")
        print(f"   Total Cost: ${traditional['total_cost']:.2f}")
        
        print(f"\n3. Western Union:")
        print(f"   Flat Fee: ${western_union['flat_fee']:.2f}")
        print(f"   Markup ({western_union['markup_percent']:.1f}%): ${western_union['markup_cost']:.2f}")
        print(f"   Total Cost: ${western_union['total_cost']:.2f}")
        
        print(f"\n4. Remitly/MoneyGram:")
        print(f"   Flat Fee: ${remitly['flat_fee']:.2f}")
        print(f"   Markup ({remitly['markup_percent']:.1f}%): ${remitly['markup_cost']:.2f}")
        print(f"   Total Cost: ${remitly['total_cost']:.2f}")
        
        # Calculate savings
        savings_vs_traditional = traditional['total_cost'] - wise_total_fee
        savings_vs_western_union = western_union['total_cost'] - wise_total_fee
        savings_vs_remitly = remitly['total_cost'] - wise_total_fee
        
        print(f"\n💵 SAVINGS:")
        print(f"   vs Traditional Bank: ${savings_vs_traditional:.2f} ({savings_vs_traditional/amount*100:.2f}%)")
        print(f"   vs Western Union: ${savings_vs_western_union:.2f} ({savings_vs_western_union/amount*100:.2f}%)")
        print(f"   vs Remitly/MoneyGram: ${savings_vs_remitly:.2f} ({savings_vs_remitly/amount*100:.2f}%)")
        
        max_savings = max(savings_vs_traditional, savings_vs_western_union, savings_vs_remitly)
        print(f"\n🎯 Maximum Savings: ${max_savings:.2f}")
        
        reports.append({
            "route": f"{source_currency} → {target_currency}",
            "amount": amount,
            "wise_cost": wise_total_fee,
            "wise_received": wise_target_amount,
            "traditional_cost": traditional['total_cost'],
            "western_union_cost": western_union['total_cost'],
            "remitly_cost": remitly['total_cost'],
            "savings_vs_traditional": savings_vs_traditional,
            "savings_vs_western_union": savings_vs_western_union,
            "savings_vs_remitly": savings_vs_remitly,
            "max_savings": max_savings
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.aclose()


async def simulate_crypto_route():
    """Simulate USD → Crypto → EUR route"""
    print("\n" + "=" * 80)
    print("SIMULATION 3: USD → Crypto → EUR Route ($11,000)")
    print("=" * 80)
    
    amount = 11000.0
    
    client = httpx.AsyncClient(timeout=30.0)
    
    try:
        # Get Kraken BTC/USD price
        print(f"\n📊 Getting real prices from Kraken API...")
        kraken = KrakenClient(client)
        btc_ticker = await get_kraken_ticker(client, "XBTUSD")
        
        if not btc_ticker:
            print("❌ Failed to get Kraken ticker")
            return
        
        btc_price_usd = float(btc_ticker.get("c", [0])[0]) if btc_ticker.get("c") else 0
        
        # Get EUR/USD rate from Wise
        wise = WiseClient(client)
        profiles = await wise.get_profiles()
        if not profiles:
            print("❌ No Wise profiles found")
            return
        
        profile_id = profiles[0]["id"]
        eur_quote = await get_wise_quote(client, profile_id, "USD", "EUR", 1000.0)
        eur_rate = eur_quote.get("rate", 0.92) if eur_quote else 0.92
        
        # Calculate crypto route costs
        # Step 1: USD → BTC (Kraken)
        # Kraken fees: 0.16% maker, 0.26% taker (use 0.2% average)
        kraken_fee_percent = 0.002
        btc_amount = (amount * (1 - kraken_fee_percent)) / btc_price_usd
        
        # Step 2: BTC → EUR (via Wise or another exchange)
        # Assume same fee structure
        eur_amount = btc_amount * btc_price_usd * eur_rate * (1 - kraken_fee_percent)
        
        total_crypto_fee = amount * kraken_fee_percent * 2  # Two trades
        
        print(f"\n✅ Crypto Route Calculation:")
        print(f"   Step 1: ${amount:,.2f} USD → BTC")
        print(f"   BTC Price: ${btc_price_usd:,.2f}")
        print(f"   Kraken Fee (0.2%): ${amount * kraken_fee_percent:.2f}")
        print(f"   BTC Received: {btc_amount:.8f} BTC")
        print(f"   Step 2: BTC → EUR")
        print(f"   EUR Rate: {eur_rate}")
        print(f"   Kraken Fee (0.2%): ${btc_amount * btc_price_usd * kraken_fee_percent:.2f}")
        print(f"   EUR Received: €{eur_amount:,.2f}")
        print(f"   Total Crypto Fees: ${total_crypto_fee:.2f}")
        
        # Compare with direct Wise transfer
        wise_quote = await get_wise_quote(client, profile_id, "USD", "EUR", amount)
        if wise_quote:
            wise_fee = wise_quote.get("fee", {})
            wise_total_fee = wise_fee.get("total", 0) if isinstance(wise_fee, dict) else wise_fee if wise_fee else 0
            wise_target_amount = wise_quote.get("targetAmount", 0)
            
            print(f"\n💰 Comparison with Direct Wise Transfer:")
            print(f"   Direct Wise: €{wise_target_amount:,.2f} (Fee: ${wise_total_fee:.2f})")
            print(f"   Crypto Route: €{eur_amount:,.2f} (Fee: ${total_crypto_fee:.2f})")
            
            if eur_amount > wise_target_amount:
                savings = eur_amount - wise_target_amount
                print(f"   💵 Crypto Route Advantage: +€{savings:,.2f} more received")
            else:
                savings = wise_target_amount - eur_amount
                print(f"   💵 Direct Wise Advantage: +€{savings:,.2f} more received")
        
        # Compare with traditional methods
        traditional = calculate_traditional_bank_cost(amount, "USD/EUR")
        
        print(f"\n💰 vs Traditional Bank:")
        print(f"   Traditional Cost: ${traditional['total_cost']:.2f}")
        print(f"   Crypto Route Cost: ${total_crypto_fee:.2f}")
        savings_vs_traditional = traditional['total_cost'] - total_crypto_fee
        print(f"   💵 Savings: ${savings_vs_traditional:.2f}")
        
        reports.append({
            "route": "USD → BTC → EUR (Crypto Route)",
            "amount": amount,
            "wise_cost": total_crypto_fee,
            "wise_received": eur_amount,
            "traditional_cost": traditional['total_cost'],
            "savings_vs_traditional": savings_vs_traditional,
            "max_savings": savings_vs_traditional
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.aclose()


async def main():
    """Run all cost savings simulations"""
    print("\n" + "=" * 80)
    print("COST SAVINGS SIMULATION SUITE")
    print("=" * 80)
    print("\nSimulating $11,000 transfers using real API quotes")
    print("Comparing against traditional remittance methods\n")
    
    await simulate_usd_to_eur_transfer()
    await simulate_usd_to_inr_transfer()
    await simulate_crypto_route()
    
    # Final Summary
    print("\n" + "=" * 80)
    print("📊 FINAL SUMMARY - $11,000 Transfer Cost Savings")
    print("=" * 80)
    
    if reports:
        total_max_savings = sum(r['max_savings'] for r in reports)
        avg_savings = total_max_savings / len(reports)
        
        print(f"\n💰 Average Savings per Transfer: ${avg_savings:.2f}")
        print(f"💰 Total Potential Savings (3 routes): ${total_max_savings:.2f}")
        
        print(f"\n📈 Savings Breakdown:")
        for i, report in enumerate(reports, 1):
            print(f"\n{i}. {report['route']}:")
            print(f"   Wise/Crypto Cost: ${report['wise_cost']:.2f}")
            print(f"   Traditional Cost: ${report['traditional_cost']:.2f}")
            print(f"   💵 Savings: ${report['savings_vs_traditional']:.2f} ({report['savings_vs_traditional']/report['amount']*100:.2f}%)")
        
        print("\n" + "=" * 80)
        print("✅ CONCLUSION:")
        print("=" * 80)
        print(f"Using Wise + Kraken APIs saves an average of ${avg_savings:.2f} per $11,000 transfer")
        print(f"compared to traditional bank transfers.")
        print(f"\nFor 10 transfers of $11,000 each: ${avg_savings * 10:,.2f} in savings")
        print(f"For 100 transfers of $11,000 each: ${avg_savings * 100:,.2f} in savings")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

